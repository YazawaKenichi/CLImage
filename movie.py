#!/usr/bin/env python3
# coding : utf-8
# image
# ディレクトリ内の動画を表示する

import cv2
import os
import sys
import copy
import PathEditor as pe
import ImageEditor as ie
from optparse import OptionParser
import random
import time
# キーボード入力の受付
import readchar
# 画面サイズの取得
import shutil
# nautilus の起動
import subprocess

def HELP():
    print("\033[2J")
    print("===== 共通で使用可能なコマンド =====")
    print("   ,    : 前の動画を再生する")
    print("   .    : 次の動画を再生する")
    print("   l    : 指定されたフレーム数先に飛ぶ")
    print("   h    : 指定されたフレーム数前に飛ぶ")
    print("   a    : はじめから再生する")
    print("   r    : ランダムに動画を再生する")
    print("   q    : 終了する")
    print("===== 動画再生中に使用可能なコマンド =====")
    print("[Space] : 一時停止")
    print("===== 一時停止中に使用可能なコマンド =====")
    print("[Space] : 再生")
    print("   j    : 次のフレームを表示する")
    print("   k    : 前のフレームを表示する")
    print("   w    : 現在のフレームを動画として保存")
    print("   d    : ランダム表示と順番表示の切り替えをする\n\t（オプションでランダム表示や逆順表示を選択したときのみ有効）")

def get_args(ui = True):
    usage = "Usage: %prog IMGPATH ... [ -v --visible ] [ -f --fullscreen ] [ -r --random ] [ -i --invert ]"
    parser = OptionParser(usage = usage)

    # -f オプションでフルスクリーン表示できる
    parser.add_option(
            "-f", "--fullscreen",
            action = "store_true",
            default = False,
            dest = "fullscreen",
            help = "GUI 表示の動画をフルスクリーンで表示する"
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
            help = "表示動画の GUI 表示をする"
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

# ディレクトリ内の動画パスをリスト型で取得
def path2list(args, ui = False):
    r_li = []
    for arg in args:
        if os.path.isdir(arg):
            # 引数がディレクトリなら
            directory = os.path.dirname(arg) + "/"
            listdir = os.listdir(directory)
            listdir.sort()
            # ディレクトリの中にある動画を取り出す
            for mov in listdir:
                if pe.ismovie(mov, ui = False):
                    r_li.append(directory + mov)
        else:
            # ディレクトリじゃないなら
            if pe.ismovie(dpath, ui = False):
                r_li.append(dpath)
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
        print(f"動画が開けません : {path}", end = "\n", file = sys.stderr)
        binary = blackscreen()
    string = f" >>> {prefix} path {end}"
    ie.showimagecli(binary, string = string, fxy = 1 / 3, fullscreen = fullscreen, ui = ui)

# 動画の再生
def mov_show(path, ui = False):
    cap = cv2.VideoCapture(path)
    # 動画が開けなかった場合
    if not cap.isOpened():
        return 1
    # 総フレーム数
    video_frame_count = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    video_len_sec = video_frame_count / video_fps
    previous = 0
    frame_index = 0
    loop = True
    while loop:
        previous = time.perf_counter()
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if ret:
            ie.showimagecli(frame, title = path, ui = ui)
        processtime = time.perf_counter() - start
        frame_index = frame_index + int(video_fps * processtime)
        if frame_index >= video_frame_count:
            loop = False

# パスのリストから動画を表示する
def list_show(li, defaultlist, fullscreen = False, ui = False):
    index = 0
    loop = True
    count = len(li)
    default = 0
    print(" " * 7, end = "")
    while loop:
        valid = False
        showingmoviepath = ""
        if not default:
            showingmoviepath = li[index]
        else:
            showingmoviepath = defaultlist[index]
        prefix = f"{defaultlist.index(showingmoviepath): >4} / {len(li): <4}"
        mov_show(showingmoviepath, fullscreen = fullscreen, prefix = prefix, ui = ui)

if __name__ == "__main__":
    optiondict, args = get_args(ui = False)
    fullscreen = optiondict.fullscreen
    random_ = optiondict.random
    invert = optiondict.invert
    ui = optiondict.visible or optiondict.fullscreen
    movpathlist = []
    for dirpath in args:
        movpathlist.extend(path2list(dirpath, ui = ui))
    if len(movpathlist) == 0:
        print("動画はありません")
        sys.exit(0)
    if ui:
        for movpath in movpathlist:
            print(movpath)
    defaultlist = copy.deepcopy(movpathlist)
    if random_:
        movpathlist = random.sample(movpathlist, len(movpathlist))
    if invert:
        movpathlist = list(reversed(movpathlist))
    list_show(movpathlist, defaultlist, fullscreen = fullscreen, ui = ui)

