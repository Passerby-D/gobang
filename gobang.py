from yaml import dump, load, Loader
from tkinter import *
import tkinter.messagebox
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pygame
import os
import random
from datetime import datetime


# 让窗口居中显示
def center_window(win: Tk, width, height):
    screenwidth = win.winfo_screenwidth()  # 获取显示屏宽度
    screenheight = win.winfo_screenheight()  # 获取显示屏高度
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)  # 设置窗口居中参数
    win.geometry(size)  # 让窗口居中显示


# 让导入的图片按固定大小缩放
def standard_image(w_, h_, png_image):
    '''
    w_ : 要适应的窗口宽
    h_ : 要适应的窗口高
    png_image : Image.open后的图片
    '''
    w, h = png_image.size  # 获取图像的原始大小
    f1 = 1.0 * w_ / w
    f2 = 1.0 * h_ / h
    factor = min([f1, f2])
    width = int(w * factor)
    height = int(h * factor)
    return png_image.resize((width, height), Image.Resampling.LANCZOS)


# 落子的位置
places = []
# 落子的圆
piece_ovals = []


# 落子
def place_piece(mode: str, round_lab: Label, event: Event, chess_info: dict, vec_x: int = 0, vec_y: int = 0):
    global round_count, winner, game_state, front_canvas, chess_canvas
    if mode == 'normal' or mode == 'time' or mode == 'ai':
        global line_num
        # 判断游戏状态，若已经结束，则不再触发event
        if game_state == 'end':
            return
        # print('x:{},y:{}'.format(event.x,event.y))
        interval = 600 / line_num
        if not (vec_x and vec_y):
            interval = 600 / line_num
            # 判断鼠标是否点在棋盘的交错点附近
            for i in range(0, line_num):
                if (1 / 5 + i) * interval < event.x < (4 / 5 + i) * interval:
                    vec_x = i + 1
                if (1 / 5 + i) * interval < event.y < (4 / 5 + i) * interval:
                    vec_y = i + 1
    if mode == 'review':
        if round_count == chess_info.get('rounds') and chess_info.get('state') != 'end':
            if chess_info.get('state') == 'time-out':
                if chess_info.get('winner') == 'black':
                    tkinter.messagebox.showinfo('对局结束', '白方超时，黑胜！')
                if chess_info.get('winner') == 'white':
                    tkinter.messagebox.showinfo('对局结束', '黑方超时，白胜！')
            if chess_info.get('state') == 'unfinished':
                tkinter.messagebox.showinfo('对局结束', '对局已结束')
            return
        line_num = chess_info.get('line_num')
        interval = 600 / line_num
        for i in range(1, line_num + 1):
            for j in range(1, line_num + 1):
                try:
                    if round_count == chess_info.get('chess').get((i, j)).get('round'):
                        vec_x = i
                        vec_y = j
                except AttributeError:
                    continue
    if vec_x and vec_y:
        # 判断是否有棋子存在，若有，无事发生or提醒，若没有，落子
        if mode != 'review' and chess.get((vec_x, vec_y)).get('state'):
            print('({},{})已经有{}棋子了'.format(vec_x, vec_y, chess.get((vec_x, vec_y)).get('state')))
        else:
            global places, round_sign
            # 根据回合数的奇偶判断下黑棋还是白棋
            if round_count % 2 == 1:
                piece_oval = chess_canvas.create_oval((vec_x - 4 / 5) * interval, (vec_y - 4 / 5) * interval,
                                                      (vec_x - 1 / 5) * interval, (vec_y - 1 / 5) * interval,
                                                      fill='black', outline='white')
                piece_ovals.append(piece_oval)
                pygame.mixer.Sound('sound effect/black_piece.wav').play().set_volume(bgm_volume/500)
                chess.update({(vec_x, vec_y): {'state': 'black', 'round': round_count}})
                if round_count == 1:
                    sign = chess_canvas.create_oval((vec_x - 0.57) * interval, (vec_y - 0.57) * interval,
                                                    (vec_x - 0.43) * interval, (vec_y - 0.43) * interval,
                                                    fill='red')
                    '''sign = chess_canvas.create_rectangle((vec_x - 4 / 5) * interval, (vec_y - 4 / 5) * interval,
                                                         (vec_x - 1 / 5) * interval, (vec_y - 1 / 5) * interval,
                                                         dash=(1, 1), outline='white')'''
                    places.append(sign)
                else:
                    chess_canvas.delete(places[-1])
                    sign = chess_canvas.create_oval((vec_x - 0.57) * interval, (vec_y - 0.57) * interval,
                                                    (vec_x - 0.43) * interval, (vec_y - 0.43) * interval,
                                                    fill='red')
                    places.append(sign)
                front_canvas.delete(round_sign)
                round_sign = front_canvas.create_line([(900, 0), (900, 50)], arrow=LAST, width=20, fill='yellow')
            else:
                piece_oval = chess_canvas.create_oval((vec_x - 4 / 5) * interval, (vec_y - 4 / 5) * interval,
                                                      (vec_x - 1 / 5) * interval, (vec_y - 1 / 5) * interval,
                                                      fill='white', outline='black')
                piece_ovals.append(piece_oval)
                pygame.mixer.Sound('sound effect/white_piece.wav').play().set_volume(bgm_volume/500)
                chess.update({(vec_x, vec_y): {'state': 'white', 'round': round_count}})
                chess_canvas.delete(places[-1])
                sign = chess_canvas.create_oval((vec_x - 0.57) * interval, (vec_y - 0.57) * interval,
                                                (vec_x - 0.43) * interval, (vec_y - 0.43) * interval,
                                                fill='red')
                places.append(sign)
                front_canvas.delete(round_sign)
                round_sign = front_canvas.create_line([(100, 0), (100, 50)], arrow=LAST, width=20, fill='yellow')
            # 若落子，判断是否游戏结束
            if victory_judge():
                pygame.mixer.Sound('sound effect/victory.wav').play().set_volume(bgm_volume/500)
                game_state = 'end'
                if round_count % 2 == 1:
                    winner = 'black'
                    tkinter.messagebox.showinfo("对局结束", "黑胜！")
                    print('黑胜')
                else:
                    winner = 'white'
                    tkinter.messagebox.showinfo("对局结束", "白胜！")
                    print('白胜')
            elif round_count == line_num * line_num:
                winner = 'draw'
                game_state = 'end'
                tkinter.messagebox.showinfo("对局结束", "已经没有子可以下啦！重新开始一局吧！")
            else:
                round_count += 1
                round_lab['text'] = round_count
                if mode == 'ai':
                    if round_count % 2 == 1:
                        vec = ai_judge('black')
                    else:
                        vec = ai_judge('white')
                    place_piece('normal', round_lab=round_lab, event=event, chess_info={}, vec_x=vec.get('vec_x'),
                                vec_y=vec.get('vec_y'))


# ai计算出应该走哪一步
def ai_judge(ai_color: str) -> dict:
    if round_count == 1:
        return {'vec_x': int(line_num / 2 + 1), 'vec_y': int(line_num / 2 + 1)}
    if ai_color == 'black':
        player_color = 'white'
    else:
        player_color = 'black'
    best_piece = {'x': [0], 'y': [0], 'score': -1}
    for i in range(1, line_num + 1):
        for j in range(1, line_num + 1):
            if not chess.get((i, j)).get('state'):
                chess.update({(i, j): {'state': player_color, 'round': round_count}})
                vertical = {'block': 0, 'length': 1, 'blank': 0}
                horizontal = {'block': 0, 'length': 1, 'blank': 0}
                left = {'block': 0, 'length': 1, 'blank': 0}
                right = {'block': 0, 'length': 1, 'blank': 0}
                for k in range(1, 5):
                    if chess.get((i, j + k)):
                        if chess.get((i, j + k)).get('state') == player_color:
                            temp_dict = {'length': vertical.get('length') + 1}
                            vertical.update(temp_dict)
                        else:
                            if chess.get((i, j + k)).get('state') == ai_color:
                                temp_dict = {'block': vertical.get('block') + 1}
                                vertical.update(temp_dict)
                                break
                            else:
                                if vertical.get('blank') == 0:
                                    if chess.get((i, j + k + 1)) and chess.get((i, j + k + 1)).get(
                                            'state') == player_color:
                                        vertical.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': vertical.get('block') + 1}
                        vertical.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i, j - k)):
                        if chess.get((i, j - k)).get('state') == player_color:
                            temp_dict = {'length': vertical.get('length') + 1}
                            vertical.update(temp_dict)
                        else:
                            if chess.get((i, j - k)).get('state') == ai_color:
                                temp_dict = {'block': vertical.get('block') + 1}
                                vertical.update(temp_dict)
                                break
                            else:
                                if vertical.get('blank') == 0:
                                    if chess.get((i, j - k - 1)) and chess.get((i, j - k - 1)).get(
                                            'state') == player_color:
                                        vertical.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': vertical.get('block') + 1}
                        vertical.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i + k, j)):
                        if chess.get((i + k, j)).get('state') == player_color:
                            temp_dict = {'length': horizontal.get('length') + 1}
                            horizontal.update(temp_dict)
                        else:
                            if chess.get((i + k, j)).get('state') == ai_color:
                                temp_dict = {'block': horizontal.get('block') + 1}
                                horizontal.update(temp_dict)
                                break
                            else:
                                if horizontal.get('blank') == 0:
                                    if chess.get((i + k + 1, j)) and chess.get((i + k + 1, j)).get(
                                            'state') == player_color:
                                        horizontal.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': horizontal.get('block') + 1}
                        horizontal.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i - k, j)):
                        if chess.get((i - k, j)).get('state') == player_color:
                            temp_dict = {'length': horizontal.get('length') + 1}
                            horizontal.update(temp_dict)
                        else:
                            if chess.get((i - k, j)).get('state') == ai_color:
                                temp_dict = {'block': horizontal.get('block') + 1}
                                horizontal.update(temp_dict)
                                break
                            else:
                                if horizontal.get('blank') == 0:
                                    if chess.get((i - k - 1, j)) and chess.get((i - k - 1, j)).get(
                                            'state') == player_color:
                                        horizontal.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': horizontal.get('block') + 1}
                        horizontal.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i + k, j + k)):
                        if chess.get((i + k, j + k)).get('state') == player_color:
                            temp_dict = {'length': left.get('length') + 1}
                            left.update(temp_dict)
                        else:
                            if chess.get((i + k, j + k)).get('state') == ai_color:
                                temp_dict = {'block': left.get('block') + 1}
                                left.update(temp_dict)
                                break
                            else:
                                if left.get('blank') == 0:
                                    if chess.get((i + k + 1, j + k + 1)) and chess.get((i + k + 1, j + k + 1)).get(
                                            'state') == player_color:
                                        left.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': left.get('block') + 1}
                        left.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i - k, j - k)):
                        if chess.get((i - k, j - k)).get('state') == player_color:
                            temp_dict = {'length': left.get('length') + 1}
                            left.update(temp_dict)
                        else:
                            if chess.get((i - k, j - k)).get('state') == ai_color:
                                temp_dict = {'block': left.get('block') + 1}
                                left.update(temp_dict)
                                break
                            else:
                                if left.get('blank') == 0:
                                    if chess.get((i - k - 1, j - k - 1)) and chess.get((i - k - 1, j - k - 1)).get(
                                            'state') == player_color:
                                        left.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': left.get('block') + 1}
                        left.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i - k, j + k)):
                        if chess.get((i - k, j + k)).get('state') == player_color:
                            temp_dict = {'length': right.get('length') + 1}
                            right.update(temp_dict)
                        else:
                            if chess.get((i - k, j + k)).get('state') == ai_color:
                                temp_dict = {'block': right.get('block') + 1}
                                right.update(temp_dict)
                                break
                            else:
                                if right.get('blank') == 0:
                                    if chess.get((i - k - 1, j + k + 1)) and chess.get((i - k - 1, j + k + 1)).get(
                                            'state') == player_color:
                                        right.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': right.get('block') + 1}
                        right.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i + k, j - k)):
                        if chess.get((i + k, j - k)).get('state') == player_color:
                            temp_dict = {'length': right.get('length') + 1}
                            right.update(temp_dict)
                        else:
                            if chess.get((i + k, j - k)).get('state') == ai_color:
                                temp_dict = {'block': right.get('block') + 1}
                                right.update(temp_dict)
                                break
                            else:
                                if right.get('blank') == 0:
                                    if chess.get((i + k + 1, j - k - 1)) and chess.get((i + k + 1, j - k - 1)).get(
                                            'state') == player_color:
                                        right.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': right.get('block') + 1}
                        right.update(temp_dict)
                        break
                defense_rank = [0, 0, 0, 0]
                defense_score = 0
                for line in [vertical, horizontal, left, right]:
                    if line.get('length') == 5 and line.get('blank') == 0:
                        defense_rank[0] += 1
                        break
                    if line.get('length') == 1 or line.get('block') == 2:
                        continue
                    if line.get('length') > 3 and line.get('block') == 0 and line.get('blank') == 0:
                        defense_rank[1] += 1
                        break
                    if (line.get('length') == 3 and line.get('block') == 0) or (
                            line.get('length') == 4 and line.get('block') == 1) and (
                            line.get('length') > 3 and line.get('block') == 0 and line.get('blank') == 1):
                        defense_rank[2] += 1
                        if line.get('length') == 3 and line.get('blank') == 1:
                            defense_rank[2] -= 0.5
                    if (line.get('length') == 2 and line.get('block') == 0) or (
                            line.get('length') == 3 and line.get('block') == 1):
                        defense_rank[3] += 1
                        if line.get('blank'):
                            defense_rank[3] -= 0.5
                if defense_rank[0]:
                    defense_score += 100000
                if defense_rank[1]:
                    defense_score += 1000
                if defense_rank[2]:
                    if defense_rank[2] > 1:
                        defense_score += 800
                    else:
                        defense_score += defense_rank[2] * 100
                if defense_rank[3]:
                    defense_score += defense_rank[3] * 10

                # 进攻分析
                chess.update({(i, j): {'state': ai_color, 'round': round_count}})
                vertical = {'block': 0, 'length': 1, 'blank': 0}
                horizontal = {'block': 0, 'length': 1, 'blank': 0}
                left = {'block': 0, 'length': 1, 'blank': 0}
                right = {'block': 0, 'length': 1, 'blank': 0}
                for k in range(1, 5):
                    if chess.get((i, j + k)):
                        if chess.get((i, j + k)).get('state') == ai_color:
                            temp_dict = {'length': vertical.get('length') + 1}
                            vertical.update(temp_dict)
                        else:
                            if chess.get((i, j + k)).get('state') == player_color:
                                temp_dict = {'block': vertical.get('block') + 1}
                                vertical.update(temp_dict)
                                break
                            else:
                                if vertical.get('blank') == 0:
                                    if chess.get((i, j + k + 1)) and chess.get((i, j + k + 1)).get('state') == ai_color:
                                        vertical.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': vertical.get('block') + 1}
                        vertical.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i, j - k)):
                        if chess.get((i, j - k)).get('state') == ai_color:
                            temp_dict = {'length': vertical.get('length') + 1}
                            vertical.update(temp_dict)
                        else:
                            if chess.get((i, j - k)).get('state') == player_color:
                                temp_dict = {'block': vertical.get('block') + 1}
                                vertical.update(temp_dict)
                                break
                            else:
                                if vertical.get('blank') == 0:
                                    if chess.get((i, j - k - 1)) and chess.get((i, j - k - 1)).get('state') == ai_color:
                                        vertical.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': vertical.get('block') + 1}
                        vertical.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i + k, j)):
                        if chess.get((i + k, j)).get('state') == ai_color:
                            temp_dict = {'length': horizontal.get('length') + 1}
                            horizontal.update(temp_dict)
                        else:
                            if chess.get((i + k, j)).get('state') == player_color:
                                temp_dict = {'block': horizontal.get('block') + 1}
                                horizontal.update(temp_dict)
                                break
                            else:
                                if horizontal.get('blank') == 0:
                                    if chess.get((i + k + 1, j)) and chess.get((i + k + 1, j)).get('state') == ai_color:
                                        horizontal.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': horizontal.get('block') + 1}
                        horizontal.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i - k, j)):
                        if chess.get((i - k, j)).get('state') == ai_color:
                            temp_dict = {'length': horizontal.get('length') + 1}
                            horizontal.update(temp_dict)
                        else:
                            if chess.get((i - k, j)).get('state') == player_color:
                                temp_dict = {'block': horizontal.get('block') + 1}
                                horizontal.update(temp_dict)
                                break
                            else:
                                if horizontal.get('blank') == 0:
                                    if chess.get((i - k - 1, j)) and chess.get((i - k - 1, j)).get('state') == ai_color:
                                        horizontal.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': horizontal.get('block') + 1}
                        horizontal.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i + k, j + k)):
                        if chess.get((i + k, j + k)).get('state') == ai_color:
                            temp_dict = {'length': left.get('length') + 1}
                            left.update(temp_dict)
                        else:
                            if chess.get((i + k, j + k)).get('state') == player_color:
                                temp_dict = {'block': left.get('block') + 1}
                                left.update(temp_dict)
                                break
                            else:
                                if left.get('blank') == 0:
                                    if chess.get((i + k + 1, j + k + 1)) and chess.get((i + k + 1, j + k + 1)).get(
                                            'state') == ai_color:
                                        left.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': left.get('block') + 1}
                        left.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i - k, j - k)):
                        if chess.get((i - k, j - k)).get('state') == ai_color:
                            temp_dict = {'length': left.get('length') + 1}
                            left.update(temp_dict)
                        else:
                            if chess.get((i - k, j - k)).get('state') == player_color:
                                temp_dict = {'block': left.get('block') + 1}
                                left.update(temp_dict)
                                break
                            else:
                                if left.get('blank') == 0:
                                    if chess.get((i - k - 1, j - k - 1)) and chess.get((i - k - 1, j - k - 1)).get(
                                            'state') == ai_color:
                                        left.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': left.get('block') + 1}
                        left.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i - k, j + k)):
                        if chess.get((i - k, j + k)).get('state') == ai_color:
                            temp_dict = {'length': right.get('length') + 1}
                            right.update(temp_dict)
                        else:
                            if chess.get((i - k, j + k)).get('state') == player_color:
                                temp_dict = {'block': right.get('block') + 1}
                                right.update(temp_dict)
                                break
                            else:
                                if right.get('blank') == 0:
                                    if chess.get((i - k - 1, j + k + 1)) and chess.get((i - k - 1, j + k + 1)).get(
                                            'state') == ai_color:
                                        right.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': right.get('block') + 1}
                        right.update(temp_dict)
                        break
                for k in range(1, 5):
                    if chess.get((i + k, j - k)):
                        if chess.get((i + k, j - k)).get('state') == ai_color:
                            temp_dict = {'length': right.get('length') + 1}
                            right.update(temp_dict)
                        else:
                            if chess.get((i + k, j - k)).get('state') == player_color:
                                temp_dict = {'block': right.get('block') + 1}
                                right.update(temp_dict)
                                break
                            else:
                                if right.get('blank') == 0:
                                    if chess.get((i + k + 1, j - k - 1)) and chess.get((i + k + 1, j - k - 1)).get(
                                            'state') == ai_color:
                                        right.update({'blank': 1})
                                        continue
                                break
                    else:
                        temp_dict = {'block': right.get('block') + 1}
                        right.update(temp_dict)
                        break
                attack_rank = [0, 0, 0, 0]
                attack_score = 0
                for line in [vertical, horizontal, left, right]:
                    if line.get('length') == 5 and line.get('blank') == 0:
                        attack_rank[0] += 1
                        break
                    if line.get('length') == 1 or line.get('block') == 2:
                        continue
                    if line.get('length') > 3 and line.get('block') == 0 and line.get('blank') == 0:
                        attack_rank[1] += 1
                        break
                    if (line.get('length') == 3 and line.get('block') == 0) or (
                            line.get('length') == 4 and line.get('block') == 1) and (
                            line.get('length') > 3 and line.get('block') == 0 and line.get('blank') == 1):
                        attack_rank[2] += 1
                    if (line.get('length') == 2 and line.get('block') == 0) or (
                            line.get('length') == 3 and line.get('block') == 1):
                        attack_rank[3] += 1
                        if line.get('blank'):
                            attack_rank[3] -= 0.5
                if attack_rank[0]:
                    attack_score += 1000000
                if attack_rank[1]:
                    attack_score += 10000
                if attack_rank[2]:
                    if attack_rank[2] > 1:
                        attack_score += 900
                    else:
                        attack_score += 100
                if attack_rank[3]:
                    attack_score += attack_rank[3] * 10

                score = 2 * attack_score + defense_score
                if best_piece.get('score') <= 0:
                    if score > best_piece.get('score'):
                        best_piece = {'x': [i], 'y': [j], 'score': score}
                else:
                    if score > best_piece.get('score') + 25:
                        best_piece = {'x': [i], 'y': [j], 'score': score}
                    elif best_piece.get('score') - 25 <= score <= best_piece.get('score') + 25 and score != 0:
                        best_piece.get('x').append(i)
                        best_piece.get('y').append(j)
                chess.update({(i, j): {'state': None, 'round': None}})
                print('i={},j={},score={}'.format(i, j, score))
    print(best_piece)
    lucky_num = random.randint(0, len(best_piece.get('x')) - 1)
    vec_dict = {'vec_x': best_piece.get('x')[lucky_num], 'vec_y': best_piece.get('y')[lucky_num]}
    return vec_dict


# 五子连成的线
victory_line = None


# 判断胜利条件
def victory_judge(draw_line: bool = True):
    global victory_line
    interval = 600 / line_num
    # 判断竖着是否有5个相同颜色的棋子
    for i in range(1, line_num + 1):
        for j in range(1, line_num - 3):
            try:
                if chess.get((i, j)).get('state'):
                    judge = True
                    for k in range(1, 5):
                        if chess.get((i, j + k)).get('state') != chess.get((i, j)).get('state'):
                            judge = False
                    if judge and draw_line:
                        victory_line = chess_canvas.create_line((i - 1 / 2) * interval, (j - 1) * interval,
                                                                (i - 1 / 2) * interval, (j + 4) * interval, fill='red',
                                                                width=5)
                        return True
            except AttributeError:
                continue
    # 判断横着是否有5个相同颜色的棋子
    for j in range(1, line_num + 1):
        for i in range(1, line_num - 3):
            try:
                if chess.get((i, j)).get('state'):
                    judge = True
                    for k in range(1, 5):
                        if chess.get((i + k, j)).get('state') != chess.get((i, j)).get('state'):
                            judge = False
                    if judge and draw_line:
                        victory_line = chess_canvas.create_line((i - 1) * interval, (j - 1 / 2) * interval,
                                                                (i + 4) * interval, (j - 1 / 2) * interval, fill='red',
                                                                width=5)
                        return True
            except AttributeError:
                continue
    # 判断斜着是否有5个相同颜色的棋子
    for i in range(1, line_num + 1):
        for j in range(1, line_num + 1):
            try:
                if chess.get((i, j)).get('state'):
                    judge = True
                    for k in range(1, 5):
                        if chess.get((i + k, j + k)).get('state') != chess.get((i, j)).get('state'):
                            judge = False
                    if judge and draw_line:
                        victory_line = chess_canvas.create_line((i - 1) * interval, (j - 1) * interval,
                                                                (i + 4) * interval, (j + 4) * interval, fill='red',
                                                                width=5)
                        return True
            except AttributeError:
                continue
    for i in range(1, line_num + 1):
        for j in range(1, line_num + 1):
            try:
                if chess.get((i, j)).get('state'):
                    judge = True
                    for k in range(1, 5):
                        if chess.get((i + k, j - k)).get('state') != chess.get((i, j)).get('state'):
                            judge = False
                    if judge and draw_line:
                        victory_line = chess_canvas.create_line((i - 1) * interval, j * interval, (i + 4) * interval,
                                                                (j - 5) * interval, fill='red', width=5)
                        return True
            except AttributeError:
                continue
    return False


# 调节背景音乐音量0~100（默认50）
bgm_volume = 50


def bgm_adjust(value):
    global bgm_volume
    bgm_volume = int(float(value))
    bgms.get(bgm_choice).set_volume(int(value) / 500)


# 调整棋盘大小（默认15x15）
line_num = 15


def difficulty_adjust(value):
    global line_num
    line_num = int(float(value))


# 调节思考时间
def thinking_time_adjust(value):
    global thinking_time
    thinking_time = float(value) * 60


# 重新布局棋盘
def chess_reset(gamemode: str, line_num: int = line_num, type: str = 'stay', ai_color: str = 'white'):
    global places, victory_line, game_state, round_count, round_sign, round_lab, chess_canvas, front_canvas, winner, black_time, white_time

    if type == 'stay':
        for oval in piece_ovals:
            chess_canvas.delete(oval)

        for i in range(1, line_num + 1):
            for j in range(1, line_num + 1):
                chess.update({(i, j): {'state': None, 'round': None}})

        if round_count % 2 == 0:
            front_canvas.delete(round_sign)
            round_sign = front_canvas.create_line([(100, 0), (100, 50)], arrow=LAST, width=20, fill='yellow')
            round_even = True
        else:
            round_even = False

        round_count = 1

        round_lab['text'] = round_count

        end_judge = False
        if game_state == 'end':
            end_judge = True
            game_state = ''
            winner = None

        if places:
            chess_canvas.delete(places[-1])
            places = []

        if victory_line:
            chess_canvas.delete(victory_line)
            victory_line = None

        if gamemode == 'time':
            black_time = thinking_time
            white_time = thinking_time
            if end_judge:
                countdown()

        if gamemode == 'ai' and ai_color == 'black':
            place_piece('normal', round_lab=round_lab, event=Event(), chess_info={}, vec_x=int(line_num / 2 + 1),
                        vec_y=int(line_num / 2 + 1))

    if type == 'leave':
        for i in range(1, line_num + 1):
            for j in range(1, line_num + 1):
                chess.update({(i, j): {'state': None, 'round': None}})

        round_count = 1

        if places:
            places = []

        if victory_line:
            victory_line = None

        if gamemode == 'time':
            black_time = thinking_time
            white_time = thinking_time

        if game_state == 'end':
            game_state = ''
            winner = None


# 重新开始 按钮功能
def click_rebutton(gamemode: str, line_num: int = line_num, ai_color: str = 'white'):
    confirm = tkinter.messagebox.askokcancel(title='重新开始', message='您确定要重新开始吗？')
    if confirm:
        chess_reset(gamemode, line_num, 'stay', ai_color)


# 悔棋 按钮功能
def click_babutton(gamemode: str, ai_color: str = 'white'):
    global round_count, winner
    if round_count == 1 or (round_count == 2 and gamemode == 'ai'):
        if gamemode == 'review':
            tkinter.messagebox.showerror('', '没有上一步棋！')
        else:
            tkinter.messagebox.showerror('', '没有棋可以悔！')
        return
    if gamemode == 'time' and white_time * black_time == 0:
        tkinter.messagebox.showinfo('', '对局已结束！')
        return
    if gamemode != 'review':
        confirm = tkinter.messagebox.askokcancel(title='悔棋', message='您确定要悔棋吗？')
    if gamemode == 'review' or confirm:
        global chess_canvas, front_canvas, round_sign, round_lab, places, line_num, victory_line, game_state
        if game_state == 'end':
            game_end = True
            game_state = ''
            chess_canvas.delete(victory_line)
            if gamemode == 'time':
                countdown()
        else:
            game_end = False
            round_count -= 1
            round_lab['text'] = round_count

        chess_canvas.delete(piece_ovals.pop())

        for piece in chess.keys():
            if chess.get(piece).get('round') == round_count:
                chess.update({piece: {'state': None, 'round': None}})

        if round_count % 2 == 1:
            front_canvas.delete(round_sign)
            round_sign = front_canvas.create_line([(100, 0), (100, 50)], arrow=LAST, width=20, fill='yellow')
        else:
            front_canvas.delete(round_sign)
            round_sign = front_canvas.create_line([(900, 0), (900, 50)], arrow=LAST, width=20, fill='yellow')

        chess_canvas.delete(places.pop())

        if gamemode == 'ai':
            if winner and winner != ai_color:
                winner = None
                return
            click_babutton('review')


# 返回初始菜单 按钮功能
def click_inbutton(gamemode: str, last_win: Tk):
    if gamemode != 'review':
        confirm = tkinter.messagebox.askokcancel(title='返回初始菜单',
                                                 message='您确定要返回初始菜单吗？您的棋局将不会被保存')
    if gamemode == 'review' or confirm:
        chess_reset(gamemode, line_num, 'leave')
        create_begin_win(last_win)


# 提示 按钮功能
def click_tibutton(gamemode: str):
    if round_count % 2 == 1:
        vec = ai_judge('black')
    else:
        vec = ai_judge('white')
    place_piece(gamemode, round_lab=round_lab, event=Event(), chess_info={}, vec_x=vec.get('vec_x'),
                vec_y=vec.get('vec_y'))


# 背景音乐选择
def bgm_select(bgm_combobox: ttk.Combobox, event):
    global bgm_choice
    bgms.get(bgm_choice).stop()
    bgm_choice = bgm_combobox.get()
    bgms.get(bgm_choice).play(-1)
    bgms.get(bgm_choice).set_volume(bgm_volume / 500)


# 选择游戏模式
def gamemode_select(buttons: list[Button], win: Tk):
    for button in buttons:
        button.destroy()
    normal_button = Button(win, text='普通模式', bg='orange', font=('华文行楷', 32), fg='white',
                           command=lambda: create_chess_win('normal', win))
    normal_button.place(relx=.5, rely=.4, anchor='center')

    time_button = Button(win, text='计时模式', bg='orange', font=('华文行楷', 32), fg='white',
                         command=lambda: create_chess_win('time', win))
    time_button.place(relx=.5, rely=.6, anchor='center')

    ai_button = Button(win, text='人机模式', bg='orange', font=('华文行楷', 32), fg='white',
                       command=lambda: ai_color_select(win))
    ai_button.place(relx=.5, rely=.8, anchor='center')


# 选择先后手
def ai_color_select(main_win: Tk):
    ai_color_win = Toplevel(main_win)
    center_window(ai_color_win, 300, 150)

    Label(ai_color_win, text='您想当黑方还是白方？', font=('仿宋', 16)).place(relx=.5, rely=.2, anchor='center')

    Button(ai_color_win, text='黑方', font=('仿宋', 16),
           command=lambda: create_chess_win('ai', main_win, 'white')).place(relx=.25, rely=.7, anchor='center')

    Button(ai_color_win, text='白方', font=('仿宋', 16),
           command=lambda: create_chess_win('ai', main_win, 'black')).place(relx=.75, rely=.7, anchor='center')

    ai_color_win.mainloop()


# 计时器
def countdown():
    global black_time, white_time, black_thinking_label, white_thinking_label, game_state, winner
    if game_state == 'end':
        return
    if round_count != 1:
        if round_count % 2 == 1:
            black_time -= 1
        else:
            white_time -= 1
    black_minute = int(black_time / 60)
    black_second = black_time % 60
    white_minute = int(white_time / 60)
    white_second = white_time % 60
    black_thinking_label['text'] = '%02d:%02d' % (black_minute, black_second)
    white_thinking_label['text'] = '%02d:%02d' % (white_minute, white_second)
    if black_time == 0:
        winner = 'white'
        game_state = 'end'
        tkinter.messagebox.showinfo('对局结束', '黑方超时，白胜！')
    if white_time == 0:
        winner = 'black'
        game_state = 'end'
        tkinter.messagebox.showinfo('对局结束', '白方超时，黑胜！')
    black_thinking_label.after(1000, countdown)


auto_state = True


def auto_play(main_win: Tk, round_lab, chess_info: dict, type: str = 'click'):
    if type == 'click':
        global auto_state
        auto_state = True
    if game_state != 'end' and auto_state:
        place_piece('review', round_lab=round_lab, event=Event(), chess_info=chess_info)
        main_win.after(1000, lambda: auto_play(main_win, round_lab, chess_info, 'auto'))


def auto_stop():
    global auto_state
    auto_state = False


# 创建保存棋谱的窗口
def create_save_win(main_win: Tk):
    if round_count == 1:
        tkinter.messagebox.showwarning('', '还没有走过子！')
        return

    save_win = tk.Toplevel(main_win)
    center_window(save_win, 400, 200)
    save_win.resizable(0, 0)

    Label(save_win, text='棋谱名：', font=('仿宋', 16)).place(x=40, y=20)

    save_entry = Entry(save_win, width=40, font=('仿宋', 12))
    save_entry.insert(0, '{}-{}-{}-{}-{}-{}'.format(datetime.now().year, datetime.now().month, datetime.now().day,
                                                    datetime.now().hour, datetime.now().minute, datetime.now().second))
    save_entry.place(relx=.5, rely=.4, anchor='center', height=30)

    save_button = Button(save_win, text='保 存', font=('仿宋', 16), command=lambda: save_chess(save_entry, save_win))
    save_button.place(relx=.25, rely=.7, anchor='center')

    cancel_button = Button(save_win, text='取 消', font=('仿宋', 16), command=lambda: save_win.destroy())
    cancel_button.place(relx=.75, rely=.7, anchor='center')

    save_win.mainloop()


# 保存棋谱
def save_chess(entry: Entry, last_win: Tk):
    chess_name = entry.get()

    if chess_name + '.yaml' in os.listdir('record'):
        tkinter.messagebox.showwarning('', '该棋谱名已存在！')
        last_win.destroy()
        return

    last_win.destroy()

    info = {}
    if game_state == 'end':
        if white_time * black_time == 0:
            state_dict = {'state': 'time-out'}
        else:
            state_dict = {'state': 'end'}
    else:
        state_dict = {'state': 'unfinished'}
    info.update(state_dict)

    info.update({'winner': winner})

    info.update({'chess': chess})

    info.update({'rounds': round_count})

    info.update({'line_num': line_num})

    with open('record/{}.yaml'.format(chess_name), 'w', encoding='utf-8') as f:
        f.write(dump(info, allow_unicode=True))
        f.close()

    tkinter.messagebox.showinfo('', '保存成功！')


def create_money_win(main_win: Tk):
    money_win = Toplevel(main_win)
    center_window(money_win, 300, 300)
    money_win.title('支付宝')
    money_win.iconbitmap('picture/alipay2.ico')

    money_image = ImageTk.PhotoImage(standard_image(280, 280, Image.open('picture/money.jpg')))
    Label(money_win, image=money_image, highlightthickness=0, borderwidth=0).place(relx=.5, rely=.5, anchor='center')

    money_win.mainloop()


chess = {}  # 记录棋盘上每个位置的点的状态(None/black/white)
round_count = 1  # 回合数
game_state = ''  # 游戏状态
winner = None  # 胜者
chess_canvas = None  # 棋盘画布
front_canvas = None  # 顶格画布

# 初始化pygame.mixer
pygame.mixer.init()
# 遍历bgm文件夹下的所有文件
bgms = {}
bgm_files = os.listdir('bgm')
for bgm_file in bgm_files:
    if '.mp3' not in bgm_file:
        bgm_files.pop(bgm_file)
for bgm_file in bgm_files:
    bgms.update({bgm_file.replace('.mp3', ''): pygame.mixer.Sound('bgm/{}'.format(bgm_file))})
bgm_choice = list(bgms.keys())[random.randint(0, len(bgm_files) - 1)]

thinking_time = 300
black_time = 300
white_time = 300
black_thinking_label = None
white_thinking_label = None
round_sign = None


# 创建读谱窗口
def create_review_win(record_combobox: ttk.Combobox, last_win: Tk):
    with open('record/{}.yaml'.format(record_combobox.get()), 'r', encoding='utf-8') as f:
        chess_info = load(f.read(), Loader=Loader)
        f.close()

    last_win.destroy()

    review_win = Tk()
    review_win.config(bg='gray')
    review_win.title("五子棋小游戏——made by Passerby_D")
    review_win.iconbitmap('picture/Passerby_D.ico')
    center_window(review_win, 1000, 800)
    review_win.resizable(0, 0)

    background_image = ImageTk.PhotoImage(Image.open('picture/background_5.jpg'))
    Label(review_win, image=background_image, highlightthickness=0, borderwidth=0).place(x=0, y=0)

    # 创建并布置顶格画布
    global round_lab, round_sign, front_canvas
    front_canvas = Canvas(review_win, bg='#4FC1CB', width=1000, height=50, highlightthickness=0)
    round_sign = front_canvas.create_line([(100, 0), (100, 50)], arrow=LAST, width=20, fill='yellow')
    front_canvas.place(x=0, y=0)
    round_lab = Label(review_win, text='1', font=('华文行楷', 36), fg='yellow', bg='#4FC1CB')
    round_lab.place(relx=.5, rely=.03125, anchor='center')

    # 导入黑方和白方的画像
    black_image = ImageTk.PhotoImage(standard_image(180, 180, Image.open('picture/^black.jpeg')))
    white_image = ImageTk.PhotoImage(standard_image(180, 180, Image.open('picture/^white.jpeg')))
    Label(review_win, image=black_image, highlightthickness=0, borderwidth=0).place(relx=.1, rely=3 / 16,
                                                                                    anchor='center')
    Label(review_win, image=white_image, highlightthickness=0, borderwidth=0).place(relx=.9, rely=3 / 16,
                                                                                    anchor='center')

    # 创建并布置棋盘画布
    global chess_canvas
    chess_canvas = Canvas(review_win, bg="orange", width=600, height=600, highlightthickness=0)
    line_num = chess_info.get('line_num')
    interval = 600 / line_num
    for i in range(0, line_num):
        chess_canvas.create_line([(interval / 2, interval * (i + 1 / 2)), (600 - interval / 2, interval * (i + 1 / 2))],
                                 fill='black', width=2)
        chess_canvas.create_line([(interval * (i + 1 / 2), interval / 2), (interval * (i + 1 / 2), 600 - interval / 2)],
                                 fill='black', width=2)
    if line_num % 2 == 1:
        chess_canvas.create_oval(295, 295, 305, 305, fill='black')
        if line_num % 4 == 3:
            chess_canvas.create_oval((-1 / 2 + 1 / 4 * (line_num + 1)) * interval - 5,
                                     (-1 / 2 + 1 / 4 * (line_num + 1)) * interval - 5,
                                     (-1 / 2 + 1 / 4 * (line_num + 1)) * interval + 5,
                                     (-1 / 2 + 1 / 4 * (line_num + 1)) * interval + 5, fill='black')
            chess_canvas.create_oval(595 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval,
                                     (-1 / 2 + 1 / 4 * (line_num + 1)) * interval - 5,
                                     605 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval,
                                     (-1 / 2 + 1 / 4 * (line_num + 1)) * interval + 5, fill='black')
            chess_canvas.create_oval((-1 / 2 + 1 / 4 * (line_num + 1)) * interval - 5,
                                     595 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval,
                                     (-1 / 2 + 1 / 4 * (line_num + 1)) * interval + 5,
                                     605 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval, fill='black')
            chess_canvas.create_oval(595 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval,
                                     595 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval,
                                     605 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval,
                                     605 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval, fill='black')
    chess_canvas.place(x=200, y=50)

    for i in range(1, line_num + 1):
        for j in range(1, line_num + 1):
            chess.update({(i, j): {'state': None, 'round': None}})

    # 创建按钮
    restart_button = Button(review_win, text='重新开始', bg='orange', font=('华文行楷', 32), fg='white',
                            command=lambda: click_rebutton('review', line_num))
    restart_button.place(relx=.125, rely=.875, anchor='center')

    back_button = Button(review_win, text='后退', bg='orange', font=('华文行楷', 32), fg='white',
                         command=lambda: click_babutton('review'))
    back_button.place(relx=.1, rely=.7, anchor='center')

    save_button = Button(review_win, text='前进', bg='orange', font=('华文行楷', 32), fg='white',
                         command=lambda: place_piece(mode='review', chess_info=chess_info, round_lab=round_lab,
                                                     event=Event()))
    save_button.place(relx=.9, rely=.7, anchor='center')

    back_button = Button(review_win, text='自动播放', bg='orange', font=('华文行楷', 32), fg='white',
                         command=lambda: auto_play(review_win, round_lab, chess_info))
    back_button.place(relx=.375, rely=.875, anchor='center')

    save_button = Button(review_win, text='停止播放', bg='orange', font=('华文行楷', 32), fg='white',
                         command=auto_stop)
    save_button.place(relx=.625, rely=.875, anchor='center')

    initial_button = Button(review_win, text='返回大厅', bg='orange', font=('华文行楷', 32), fg='white',
                            command=lambda: click_inbutton('review', review_win))
    initial_button.place(relx=.875, rely=.875, anchor='center')

    review_win.mainloop()


# 创建读谱选择小窗口
def create_record_select_win(main_win: Tk):
    if len(os.listdir('record')) == 0:
        tkinter.messagebox.showerror('未找到棋谱', '您没有可查询的棋谱！')
        return
    record_select_win = Toplevel(main_win)
    center_window(record_select_win, 300, 150)
    record_select_win.resizable(0, 0)

    Label(record_select_win, text='请选择您想查看的棋谱：', font=('仿宋', 12)).place(x=20, y=10)

    record_combobox = ttk.Combobox(record_select_win, font=('仿宋'), height=100, width=30, state='readonly')
    record_tuple = ()
    record_files = os.listdir('record')
    for record_file in record_files:
        if '.yaml' in record_file:
            record_tuple += (record_file.replace('.yaml', ''),)
    record_combobox['value'] = record_tuple
    record_combobox.current(random.randint(0, len(record_tuple) - 1))
    record_combobox.place(relx=.5, rely=.4, anchor='center')

    select_button = Button(record_select_win, text='确定', font=('仿宋', 12), width=10,
                           command=lambda: create_review_win(record_combobox, main_win))
    select_button.place(relx=.5, rely=.8, anchor='center')

    record_select_win.mainloop()


# 创建主游戏窗口
def create_chess_win(gamemode: str, last_win: Tk, ai_color: str = 'white'):
    global chess_canvas, front_canvas, round_sign, round_lab
    last_win.destroy()
    # 创建游戏窗口
    chess_win = Tk()
    chess_win.config(bg='gray')
    chess_win.title("五子棋小游戏——made by Passerby_D")
    chess_win.iconbitmap('picture/Passerby_D.ico')
    center_window(chess_win, 1000, 800)
    chess_win.resizable(0, 0)

    background_image = ImageTk.PhotoImage(Image.open('picture/background_5.jpg'))
    Label(chess_win, image=background_image, highlightthickness=0, borderwidth=0).place(x=0, y=0)

    if gamemode == 'time':
        print('time')
        global black_thinking_label, white_thinking_label, black_time, white_time
        black_time = thinking_time
        white_time = thinking_time

        black_thinking_label = Label(chess_win, bg='#4FC1CB', font=('楷体', 30), fg='black', width=10, height=3,
                                     highlightthickness=0, borderwidth=0)
        white_thinking_label = Label(chess_win, bg='#4FC1CB', font=('楷体', 30), fg='white', width=10, height=3,
                                     highlightthickness=0, borderwidth=0)
        black_thinking_label.place(x=0, y=320)
        white_thinking_label.place(x=800, y=320)
        countdown()

    # 导入黑方和白方的画像
    black_image = ImageTk.PhotoImage(standard_image(180, 180, Image.open('picture/^black.jpeg')))
    white_image = ImageTk.PhotoImage(standard_image(180, 180, Image.open('picture/^white.jpeg')))
    Label(chess_win, image=black_image, highlightthickness=0, borderwidth=0).place(relx=.1, rely=3 / 16,
                                                                                   anchor='center')
    Label(chess_win, image=white_image, highlightthickness=0, borderwidth=0).place(relx=.9, rely=3 / 16,
                                                                                   anchor='center')

    # 创建并布置顶格画布
    front_canvas = Canvas(chess_win, bg='#4FC1CB', width=1000, height=50, highlightthickness=0)
    round_sign = front_canvas.create_line([(100, 0), (100, 50)], arrow=LAST, width=20, fill='yellow')
    front_canvas.place(x=0, y=0)
    round_lab = Label(chess_win, text='1', font=('楷体', 36), fg='yellow', bg='#4FC1CB')
    round_lab.place(relx=.5, rely=.03125, anchor='center')

    # 创建按钮
    tips_button = Button(chess_win, text='提示', bg='orange', font=('华文行楷', 32), fg='white',
                         command=lambda: click_tibutton(gamemode))
    tips_button.place(relx=.9, rely=.7, anchor='center')

    restart_button = Button(chess_win, text='重新开始', bg='orange', font=('华文行楷', 32), fg='white',
                            command=lambda: click_rebutton(gamemode, line_num, ai_color))
    restart_button.place(relx=.125, rely=.875, anchor='center')

    back_button = Button(chess_win, text='  悔    棋  ', bg='orange', font=('华文行楷', 32), fg='white',
                         command=lambda: click_babutton(gamemode, ai_color))
    back_button.place(relx=.375, rely=.875, anchor='center')

    save_button = Button(chess_win, text='保存棋谱', bg='orange', font=('华文行楷', 32), fg='white',
                         command=lambda: create_save_win(chess_win))
    save_button.place(relx=.625, rely=.875, anchor='center')

    initial_button = Button(chess_win, text='返回大厅', bg='orange', font=('华文行楷', 32), fg='white',
                            command=lambda: click_inbutton(gamemode, chess_win))
    initial_button.place(relx=.875, rely=.875, anchor='center')

    for i in range(1, line_num + 1):
        for j in range(1, line_num + 1):
            chess.update({(i, j): {'state': None, 'round': None}})

    # 创建并布置棋盘画布
    chess_canvas = Canvas(chess_win, bg="orange", width=600, height=600, highlightthickness=0)
    interval = 600 / line_num
    for i in range(0, line_num):
        chess_canvas.create_line([(interval / 2, interval * (i + 1 / 2)), (600 - interval / 2, interval * (i + 1 / 2))],
                                 fill='black', width=2)
        chess_canvas.create_line([(interval * (i + 1 / 2), interval / 2), (interval * (i + 1 / 2), 600 - interval / 2)],
                                 fill='black', width=2)
    if line_num % 2 == 1:
        chess_canvas.create_oval(295, 295, 305, 305, fill='black')
        if line_num % 4 == 3:
            chess_canvas.create_oval((-1 / 2 + 1 / 4 * (line_num + 1)) * interval - 5,
                                     (-1 / 2 + 1 / 4 * (line_num + 1)) * interval - 5,
                                     (-1 / 2 + 1 / 4 * (line_num + 1)) * interval + 5,
                                     (-1 / 2 + 1 / 4 * (line_num + 1)) * interval + 5, fill='black')
            chess_canvas.create_oval(595 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval,
                                     (-1 / 2 + 1 / 4 * (line_num + 1)) * interval - 5,
                                     605 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval,
                                     (-1 / 2 + 1 / 4 * (line_num + 1)) * interval + 5, fill='black')
            chess_canvas.create_oval((-1 / 2 + 1 / 4 * (line_num + 1)) * interval - 5,
                                     595 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval,
                                     (-1 / 2 + 1 / 4 * (line_num + 1)) * interval + 5,
                                     605 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval, fill='black')
            chess_canvas.create_oval(595 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval,
                                     595 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval,
                                     605 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval,
                                     605 - (-1 / 2 + 1 / 4 * (line_num + 1)) * interval, fill='black')
    chess_canvas.bind('<Button-1>',
                      lambda event: place_piece(mode=gamemode, round_lab=round_lab, event=event, chess_info={}))
    chess_canvas.place(x=200, y=50)

    if gamemode == 'ai' and ai_color == 'black':
        place_piece('normal', round_lab=round_lab, event=Event(), chess_info={}, vec_x=int(line_num / 2 + 1),
                    vec_y=int(line_num / 2 + 1))

    chess_win.mainloop()


# 创建设置窗口
def create_setting_win(last_win: Tk):
    last_win.destroy()
    setting_win = Tk()
    setting_win.config(bg='gray')
    setting_win.title('设置')
    setting_win.iconbitmap('picture/Passerby_D.ico')
    center_window(setting_win, 400, 600)
    setting_win.resizable(0, 0)

    background = Image.open('picture/background_star.jpeg')
    background_image = ImageTk.PhotoImage(background)
    Label(setting_win, image=background_image, highlightthickness=0, borderwidth=0).place(x=0, y=0)

    bgm_combobox = ttk.Combobox(setting_win, height=100, width=32, state='readonly')
    bgm_tuple = ()
    for bgm in bgms:
        bgm_tuple += (bgm,)
    bgm_combobox['value'] = bgm_tuple
    bgm_combobox.current(list(bgms.keys()).index(bgm_choice))
    bgm_combobox.bind("<<ComboboxSelected>>", lambda event: bgm_select(bgm_combobox, event))
    bgm_combobox.place(x=50, y=50)

    bgm_scale = Scale(setting_win, label='背景音乐', bg='lightskyblue', font=('华文行楷', 15), fg='black', from_=0,
                      to=100,
                      orient=tk.HORIZONTAL, length=300, tickinterval=10, borderwidth=0, highlightthickness=0,
                      command=bgm_adjust)
    bgm_scale.set(bgm_volume)
    bgm_scale.place(x=50, y=100)

    difficulty_scale = Scale(setting_win, label='棋盘大小', bg='lightskyblue', font=('华文行楷', 15), fg='black',
                             from_=7, to=27,
                             orient=tk.HORIZONTAL, length=300, tickinterval=4, borderwidth=0, highlightthickness=0,
                             command=difficulty_adjust)
    difficulty_scale.set(line_num)
    difficulty_scale.place(x=50, y=200)

    thinking_time_scale = Scale(setting_win, label='思考时间（min）', bg='lightskyblue', font=('华文行楷', 15),
                                fg='black', from_=1, to=10,
                                orient=tk.HORIZONTAL, length=300, tickinterval=1, borderwidth=0, highlightthickness=0,
                                command=thinking_time_adjust)
    thinking_time_scale.set(thinking_time / 60)
    thinking_time_scale.place(x=50, y=300)

    exit_button = Button(setting_win, bg='orange', text='返回大厅', font=('华文行楷', 32), fg='white', borderwidth=0,
                         highlightthickness=0, command=lambda: create_begin_win(setting_win))
    exit_button.place(relx=.5, rely=.8, anchor='center')
    setting_win.mainloop()


# 创建初始界面窗口
def create_begin_win(last_win: Tk = None):
    if last_win:
        last_win.destroy()
    # 创建初始窗口
    begin_win = Tk()
    begin_win.config(bg='gray')
    begin_win.title('五子棋小游戏——made by Passerby_D')
    begin_win.iconbitmap('picture/Passerby_D.ico')
    center_window(begin_win, 400, 600)
    begin_win.resizable(0, 0)

    background = Image.open('picture/background_bamboo.jpeg')
    background_image = ImageTk.PhotoImage(background)
    Label(begin_win, image=background_image, highlightthickness=0, borderwidth=0).place(x=0, y=0)

    money_button = Button(begin_win, text='赞助开发者', bg='yellow', command=lambda: create_money_win(begin_win))
    money_button.place(x=10, y=10)

    begin_button = Button(begin_win, text='开始游戏', bg='orange', font=('华文行楷', 32), fg='white', width=12,
                          height=1)
    begin_button.place(relx=.5, rely=3 / 8, anchor='center')

    review_button = Button(begin_win, text='  打     谱  ', bg='orange', font=('华文行楷', 32), fg='white', width=12,
                           height=1, command=lambda: create_record_select_win(begin_win))
    review_button.place(relx=.5, rely=13 / 24, anchor='center')

    setting_button = Button(begin_win, text='  设    置  ', bg='orange', font=('华文行楷', 32), fg='white', width=12,
                            height=1, command=lambda: create_setting_win(begin_win))
    setting_button.place(relx=.5, rely=17 / 24, anchor='center')

    exit_button = Button(begin_win, text='退出游戏', bg='orange', font=('华文行楷', 32), fg='white', width=12,
                         height=1, command=lambda: begin_win.destroy())
    exit_button.place(relx=.5, rely=7 / 8, anchor='center')

    begin_win_buttons = [begin_button, review_button, setting_button, exit_button]
    begin_button['command'] = lambda: gamemode_select(begin_win_buttons, begin_win)

    begin_win.mainloop()


if __name__ == "__main__":
    bgms.get(bgm_choice).play(-1)
    bgms.get(bgm_choice).set_volume(bgm_volume / 500)
    create_begin_win()
