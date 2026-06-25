# RogueTech Codex - Install Guide

RogueTech Codex is a standalone offline wiki for the RogueTech BattleTech mod.  
It runs entirely on your machine - no internet connection required after installation.

---

## Download

Go to the [Releases page](../../releases) and download the latest release:

- `RogueTech-Codex-vX.Y.Z.zip` - the application (includes portraits)

---

## Install

Extract `RogueTech-Codex-vX.Y.Z.zip` to a folder of your choice, for example:

```
C:\Tools\RogueTech-Codex\
```

You should see `RogueTech-Codex.exe` inside.

---

## Run

Double-click `RogueTech-Codex.exe`.

A terminal window will open briefly, then your default browser will open automatically to:

```
http://localhost:8765
```

**Leave the terminal window open** while using the app - closing it stops the server.

To stop the app, close the terminal window or press `Ctrl+C` in it.

---

## Troubleshooting

**Browser doesn't open automatically**  
Open your browser manually and go to `http://localhost:8765`.

**"Windows protected your PC" (SmartScreen warning)**  
Click **More info → Run anyway**. This appears because the exe is not code-signed.

**Port 8765 already in use**  
Another application is using that port. Close it and try again.
