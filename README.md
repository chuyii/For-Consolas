## PowerShell

```
> python -m venv .venv
> Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
> .venv\Scripts\activate.ps1
> pip install flake8 black
```

## GNU/Linux

事前に fontforge をインストールしておく。
以下コマンドで fontforge のバージョンが表示されることを確認する。

```
$ python -c "import fontforge; print(fontforge.version())"
20230101
```

```
$ python -m venv .venv
$ ln -s $(python -c "import fontforge; print(fontforge.__file__)") .venv/lib/python3.*/site-packages
$ ln -s $(python -c "import psMat; print(psMat.__file__)") .venv/lib/python3.*/site-packages
$ source .venv/bin/activate
$ pip install flake8 black
$ pip install mypy
$ stubgen -m fontforge -o .venv/lib/python3.*/site-packages
$ stubgen -m psMat -o .venv/lib/python3.*/site-packages
$ ./prepare.sh
$ ./main.py --prepare
$ ./nerd-fonts/font-patcher -c -s -l half.ttf
$ ./nerd-fonts/font-patcher -c -s -l full.ttf
$ ./main.py --generate regular
$ ./main.py --generate bold
$ ./main.py --generate inconsolata
```
