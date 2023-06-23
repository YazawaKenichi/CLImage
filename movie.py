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
def path2list(arg, ui = False):
    r_li = []
    if os.path.isdir(arg):
        # 引数がディレクトリなら
        directory = os.path.dirname(arg) + "/"
        listdir = os.listdir(directory)
        listdir.sort()
        # ディレクトリの中にある動画を取り出す
        for mov in listdir:
            if pe.ismovie(mov, ui = ui):
                r_li.append(directory + mov)
    if os.path.isfile(arg):
        # ディレクトリじゃないなら
        if pe.ismovie(arg, ui = ui):
            r_li.append(arg)
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

# 動画の再生
def mov_show(path, ui = False):
    cap = cv2.VideoCapture(path)
    # 動画が開けなかった場合
    if not cap.isOpened():
        return 1
    # 総フレーム数
    video_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    video_len_sec = video_frame_count / video_fps
    loop = True
    previous = 0
    frame_index = 0
    processtime = 0
    sprocesstime = 0
    # カーソルより後ろの画面消去
    # print(f"\x1b[2J", end = "")
    start_time = time.perf_counter()
    while loop:
        # 開始からの経過時間の計算
        sprocesstime = time.perf_counter() - start_time
        # 経過時間から今どのフレームを表示するべきかの計算
        frame_index = round(video_fps * sprocesstime)
        debug = ""
        if frame_index >= video_frame_count:
            loop = False
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = cap.read()
            title = f"{path}, {int(100*frame_index/video_frame_count): >3}, {frame_index} / {video_frame_count}\n"
            if ret:
                # (1, 1) に移動
                # print(f"\x1b[1;1H", end = "")
                h, w = ie.showimagecli(frame, title = title + debug, ui = False)
                print(f"\x1b[{h}F\r", end = "")
        """
        key_str = str(readchar.readkey())
        if key_str == "q":
            # (1, 1) に移動
            # print(f"\x1b[1;1H", end = "")
            # カーソルより後ろの画面消去
            print(f"\x1b[2J", end = "")
            loop = False
        """

# パスのリストから動画を表示する
def list_show(li, defaultlist, fullscreen = False, ui = False):
    index = 0
    loop = True
    count = len(li)
    default = 0
    while loop:
        valid = False
        showingmoviepath = ""
        if not default:
            showingmoviepath = li[index]
        else:
            showingmoviepath = defaultlist[index]
        prefix = f"{defaultlist.index(showingmoviepath): >4} / {len(li): <4}"
        mov_show(showingmoviepath, ui = ui)
        loop = False

if __name__ == "__main__":
    optiondict, args = get_args(ui = False)
    fullscreen = optiondict.fullscreen
    random_ = optiondict.random
    invert = optiondict.invert
    ui = optiondict.visible or optiondict.fullscreen
    movpathlist = []
    for arg in args:
        movpathlist.extend(path2list(arg, ui = False))
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

