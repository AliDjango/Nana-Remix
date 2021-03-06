import os
import shutil
import sys

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError, NoSuchPathError
from pyrogram import filters

from nana import app, Command, AdminSettings, OFFICIAL_BRANCH, REPOSITORY, edrep
from nana.__main__ import restart_all, except_hook
from nana.assistant.updater import update_changelog

__MODULE__ = "Updater"
__HELP__ = """
You want to update latest version?
Easy, just type like bellow

──「 **Check update** 」──
-> `update`
Only check update if avaiable

──「 **Update bot** 」──
-> `update now`
Update your bot to latest version
"""


async def gen_chlog(repo, diff):
    changelog = ""
    d_form = "%H:%M - %d/%m/%y"
    for cl in repo.iter_commits(diff):
        changelog += f"• [{cl.committed_datetime.strftime(d_form)}]: {cl.summary} <{cl.author}>\n"
    return changelog


async def initial_git(repo):
    isexist = os.path.exists("nana-old")
    if isexist:
        shutil.rmtree("nana-old")
    os.mkdir("nana-old")
    os.rename("nana", "nana-old/nana")
    os.rename(".gitignore", "nana-old/.gitignore")
    os.rename("LICENSE", "nana-old/LICENSE")
    os.rename("README.md", "nana-old/README.md")
    os.rename("requirements.txt", "nana-old/requirements.txt")
    os.rename("Procfile", "nana-old/Procfile")
    os.rename("runtime.txt", "nana-old/runtime.txt")
    update = repo.create_remote("master", REPOSITORY)
    update.pull("master")
    os.rename("nana-old/nana/config.py", "nana/config.py")
    shutil.rmtree("nana/session/")
    os.rename("nana-old/nana/session/", "nana/session/")


@app.on_message(filters.user(AdminSettings) & filters.command("update", Command))
async def updater(client, message):
    initial = False
    try:
        repo = Repo()
    except NoSuchPathError as error:
        await edrep(
            message,
            text=f"**Update failed!**\n\nError:\n`directory {error} is not found`",
        )
        return
    except InvalidGitRepositoryError:
        repo = Repo.init()
        initial = True
    except GitCommandError as error:
        await edrep(message, text=f"**Update failed!**\n\nError:\n`{error}`")
        return

    if initial:
        if len(message.text.split()) != 2:
            await edrep(
                message,
                text="Your git workdir is missing!\nBut i can repair and take new latest update for you.\nJust do `update "
                "now` to repair and take update!",
            )
            return
        elif len(message.text.split()) == 2 and message.text.split()[1] == "now":
            try:
                await initial_git(repo)
            except Exception as err:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                await edrep(message, text=f"**Error:**\n{err}")
                await except_hook(exc_type, exc_obj, exc_tb)
                return
            await edrep(message, text="Successfully Updated!\nBot is restarting...")
            await update_changelog(
                "-> **WARNING**: Bot has been created a new git and sync to latest version, your old files is in nana-old"
            )
            await restart_all()
            return

    brname = repo.active_branch.name
    if brname not in OFFICIAL_BRANCH:
        await edrep(
            message,
            text=f"**[UPDATER]:** Looks like you are using your own custom branch ({brname}). in that case, Updater is unable to identify which branch is to be merged. please checkout to any official branch",
        )
        return
    try:
        repo.create_remote("upstream", REPOSITORY)
    except BaseException:
        pass

    upstream = repo.remote("upstream")
    upstream.fetch(brname)
    try:
        changelog = await gen_chlog(repo, f"HEAD..upstream/{brname}")
    except Exception as err:
        if "fatal: bad revision" in str(err):
            try:
                await initial_git(repo)
            except Exception as err:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                await edrep(message, text=f"**Error:**\n{err}")
                await except_hook(exc_type, exc_obj, exc_tb)
                return
            await edrep(message, text="Successfully Updated!\nBot is restarting...")
            await update_changelog(
                "-> **WARNING**: Bot has been created a new git and sync to latest version, your old files is in nana-old"
            )
            await restart_all()
            return
        exc_type, exc_obj, exc_tb = sys.exc_info()
        await edrep(
            message,
            text="An error has accured!\nPlease see your Assistant for more information!",
        )
        await except_hook(exc_type, exc_obj, exc_tb)
        return

    if not changelog:
        await edrep(message, text=f"Nana is up-to-date with branch **{brname}**\n")
        return

    if len(message.text.split()) != 2:
        changelog_str = (
            f"To update latest changelog, do\n-> `update now`\n\n**New UPDATE available for [{brname}]:\n"
            f"\nCHANGELOG:**\n`{changelog}` "
        )
        if len(changelog_str) > 4096:
            await edrep(
                message, text="`Changelog is too big, view the file to see it.`"
            )
            with open("nana/cache/output.txt", "w+") as file:
                file.write(changelog_str)
            await client.send_document(
                message.chat.id,
                "nana/cache/output.txt",
                reply_to_message_id=message.message_id,
                caption="`Changelog file`",
            )
            os.remove("nana/cache/output.txt")
        else:
            await edrep(message, text=changelog_str)
        return
    elif len(message.text.split()) == 2 and message.text.split()[1] == "now":
        await edrep(message, text="`New update found, updating...`")
        try:
            upstream.pull(brname)
            await edrep(message, text="Successfully Updated!\nBot is restarting...")
        except GitCommandError:
            repo.git.reset("--hard")
            repo.git.clean("-fd", "nana/modules/")
            repo.git.clean("-fd", "nana/assistant/")
            repo.git.clean("-fd", "nana/helpers/")
            await edrep(message, text="Successfully Updated!\nBot is restarting...")
        await update_changelog(changelog)
        await restart_all()
    else:
        await edrep(
            message,
            text="Usage:\n-> `update` to check update\n-> `update now` to update latest commits\nFor more information ",
        )
