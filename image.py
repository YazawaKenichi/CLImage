#!/usr/bin/env python3
# coding : utf-8
# image
# ディレクトリ内の画像を表示する

import cv2
import os
import sys
import copy
import PathEditor as pe
import ImageEditor as ie
from optparse import OptionParser
import random
# キーボード入力の受付
import readchar
# 画面サイズの取得
import shutil
# nautilus の起動
import subprocess

def HELP():
    print("\033[2J")
    print("===== 画像表示中に使用可能なコマンド =====")
    print("j : 次の画像を表示する")
    print("k : 前の画像を表示する")
    print("r : ランダムに画像を表示する")
    print("d : ランダム表示と順番表示の切り替えをする\n\t（オプションでランダム表示や逆順表示を選択したときのみ有効）")
    print("q : 終了する")
    print("h : このヘルプの表示をする")

def get_args(ui = True):
    usage = "Usage: %prog IMGPATH ... [ -v --visible ] [ -f --fullscreen ] [ -r --random ] [ -i --invert ]"
    parser = OptionParser(usage = usage)

    # -f オプションでフルスクリーン表示できる
    parser.add_option(
            "-f", "--fullscreen",
            action = "store_true",
            default = False,
            dest = "fullscreen",
            help = "GUI 表示の画像をフルスクリーンで表示する"
            )
    # -r オプションでランダムな順番に表示できる
    parser.add_option(
            "-r", "--random",
            action = "store_true",
            default = False,
            dest = "random",
            help = "ランダムな順番にする"
            )
    # -v オプションで処理詳細を表示できる
    parser.add_option(
            "-v", "--visible",
            action = "store_true",
            default = False,
            dest = "visible",
            help = "表示画像の GUI 表示をする"
            )
    # -i オプションで逆順に表示できる
    parser.add_option(
            "-i", "--invert",
            action = "store_true",
            default = False,
            dest = "invert",
            help = "逆順に表示する"
            )

    if ui:
        optdict, args = parser.parse_args()
        print("[args] ", optdict, args)
    return parser.parse_args()

# ディレクトリ内の画像パスをリスト型で取得
def path2list(dirpath, ui = False):
    r_li = []
    if os.path.isdir(dirpath):
        if not dirpath[-1] == "/":
            dirpath = dirpath + "/"
        listdir = os.listdir(dirpath)
        listdir.sort()
        for im in listdir:
            if pe.isimage(im, ui = False):
                r_li.append(dirpath + im)
    if pe.isimage(dirpath, ui = False):
        r_li.append(dirpath)
    return r_li

def blackscreen(width = 256, height = 256):
    # 色相
    h = 0
    # 彩度
    s = 0
    # 明度
    v = 1 / 4
    image_ = hsv_gen(h, s, v, width, height)
    imageheight, imagewidth = image_.shape[:2]
    text = "No Image"
    thickness = 4
    font_size = imagewidth / 10 / len(text)
    textheight = font_size * 2 / 1
    x = int(imagewidth * 2.5 / 100)
    y = 255 - int(imageheight / 2 - textheight / 2)
    position = (x, y)
    cv2.putText(image_, text, position, cv2.FONT_HERSHEY_PLAIN, font_size, (255, 255, 255), thickness, cv2.LINE_AA)
    return image_

# 画像を読み取って解像度下げてグレイスケール化して値によって文字を変化させる
def im_show(path, fullscreen = False, prefix = "", end = "\n", ui = False):
    binary = cv2.imread(path)
    if binary is None:
        print(f"画像が開けません : {path}", end = "\n", file = sys.stderr)
        binary = blackscreen()
    string = f" >>> {prefix} path {end}"
    ie.showimagecli(binary, string = string, fxy = 1 / 3, fullscreen = fullscreen, ui = ui)

# パスのリストから画像を表示する
def list_show(li, defaultlist, fullscreen = False, ui = False):
    index = 0
    loop = True
    count = len(li)
    default = 0
    print(" " * 7, end = "")
    while loop:
        valid = False
        if not default:
            showingimage = li[index]
        else:
            showingimage = defaultlist[index]
        prefix = f"{defaultlist.index(showingimage): >4} / {len(li): <4}"
        im_show(showingimage, fullscreen = fullscreen, prefix = prefix, ui = ui)
        # 特定のキーが入力されるまでループ
        while not valid:
            key = ""
            if ui:
                key = cv2.waitKey(1)
            else:
                key_str = readchar.readkey()
                # sys.stdout.write(key_str)
                try:
                    key = ord(key_str)
                except TypeError:
                    key = 0

            if key == ord("q"):
                print(f"\033[2J\033[{shutil.get_terminal_size().lines}F", end = "\033[0J")
                loop = False
                valid = True
            if key == ord("j"):
                print("  next ", end = "")
                if index + 1 >= count:
                    index = 0
                else:
                    index = index + 1
                loop = True
                valid = True
            if key == ord("k"):
                print("preview", end = "")
                if index <= 0:
                    index = count - 1
                else:
                    index = index - 1
                loop = True
                valid = True
            if key == ord("r"):
                print(" random ", end = "")
                index = random.randrange(count)
                loop = True
                valid = True
            if key == ord("d"):
                if default:
                    default = 0
                    index = li.index(defaultlist[index])
                else:
                    default = 1
                    index = defaultlist.index(li[index])
                loop = True
                valid = False
            if key == ord("x"):
                print(" remove ", end = "")
                remove(showingimage)
                index = index + 1
                loop = True
                valid = True
            if key == ord("f"):
                print("  full  ", end = "")
                if not ui:
                    ui = True
                    fullscreen = True
                else :
                    if not fullscreen:
                        fullscreen = True
                    else:
                        fullscreen = False
                loop = True
                valid = True
            if key == ord("v"):
                print(" visible", end = "")
                if not ui:
                    ui = True
                else:
                    ui = False
                    cv2.destroyAllWindows()
                loop = True
                valid = True
            if key == ord("e"):
                # 試験的
                print("explorer", end = "")
                # 以下の行でプログラム全体が停止することに注意
                subprocess.run(f"dbus-launch nautilus {showingimage}", shell = True)
                # よってこの先には行けない
                loop = False
                valid = False
            if key == ord("h"):
                print("  help  ", end = "")
                HELP()
                loop = True
                valid = False
        if ui:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    optiondict, args = get_args(ui = False)
    fullscreen = optiondict.fullscreen
    random_ = optiondict.random
    invert = optiondict.invert
    ui = optiondict.visible or optiondict.fullscreen
    impathlist = []
    for dirpath in args:
        impathlist.extend(path2list(dirpath, ui = ui))
    if len(impathlist) == 0:
        print("画像はありません")
        sys.exit(0)
    if ui:
        for impath in impathlist:
            print(impath)
    defaultlist = copy.deepcopy(impathlist)
    if random_:
        impathlist = random.sample(impathlist, len(impathlist))
    if invert:
        impathlist = list(reversed(impathlist))
    list_show(impathlist, defaultlist, fullscreen = fullscreen, ui = ui)

