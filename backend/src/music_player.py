import pygame
import os
from typing import List

class MusicPlayer:
    def __init__(self):
        # 初始化pygame的音频模块
        pygame.mixer.init()
        
        # 播放器状态管理
        self.playlist: List[str] = []  # 播放列表
        self.current_song_index: int = -1  # 当前播放曲目索引
        self.is_playing: bool = False  # 是否正在播放

    # TODO: 根据主要情绪加载不同的播放列表
    def load_playlist(self, folder_path: str) -> None:
        """
        加载指定文件夹下的音频文件到播放列表
        支持格式：mp3, wav, ogg
        """
        supported_formats = ('.mp3', '.wav', '.ogg')
        self.playlist.clear()
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            print(f"错误：文件夹 {folder_path} 不存在！")
            return
        
        # 遍历文件夹，收集音频文件
        for file in os.listdir(folder_path):
            if file.lower().endswith(supported_formats):
                self.playlist.append(os.path.join(folder_path, file))
        
        if not self.playlist:
            print("警告：指定文件夹中未找到支持的音频文件！")
        else:
            print(f"成功加载 {len(self.playlist)} 首曲目到播放列表")

    def play_song(self, index: int = None) -> None:
        """
        播放指定索引的曲目，若无索引则播放当前/第一首
        """
        # 处理播放列表为空的情况
        if not self.playlist:
            print("错误：播放列表为空，请先加载音频文件！")
            return
        
        # 确定要播放的曲目索引
        if index is not None:
            if 0 <= index < len(self.playlist):
                self.current_song_index = index
            else:
                print(f"错误：索引 {index} 超出播放列表范围！")
                return
        elif self.current_song_index == -1:
            # 首次播放，默认播放第一首
            self.current_song_index = 0
        
        # 停止当前播放的音频（如果有）
        pygame.mixer.music.stop()
        
        # 加载并播放指定曲目
        song_path = self.playlist[self.current_song_index]
        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.is_playing = True
            print(f"正在播放：{os.path.basename(song_path)}")
        except Exception as e:
            print(f"播放失败：{e}")
            self.is_playing = False

    def pause_song(self) -> None:
        """暂停当前播放的曲目"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            print("已暂停播放")

    def resume_song(self) -> None:
        """恢复暂停的曲目"""
        if not self.is_playing and self.current_song_index != -1:
            pygame.mixer.music.unpause()
            self.is_playing = True
            print("恢复播放")

    def stop_song(self) -> None:
        """停止当前播放的曲目"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.current_song_index = -1
        print("已停止播放")

    def next_song(self) -> None:
        """播放下一首曲目（循环）"""
        if not self.playlist:
            print("错误：播放列表为空！")
            return
        
        # 计算下一首索引（循环播放）
        self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
        self.play_song(self.current_song_index)

    def prev_song(self) -> None:
        """播放上一首曲目（循环）"""
        if not self.playlist:
            print("错误：播放列表为空！")
            return
        
        # 计算上一首索引（循环播放）
        self.current_song_index = (self.current_song_index - 1) % len(self.playlist)
        self.play_song(self.current_song_index)

# 测试播放器
if __name__ == "__main__":
    # 创建播放器实例
    player = MusicPlayer()
    
    # 替换为你的音频文件文件夹路径（绝对路径/相对路径均可）
    music_folder = "./music"  # 示例：当前目录下的music文件夹
    player.load_playlist(music_folder)
    
    # 简单的交互演示
    print("\n=== 音乐播放器操作说明 ===")
    print("1. 播放：play")
    print("2. 暂停：pause")
    print("3. 恢复：resume")
    print("4. 下一首：next")
    print("5. 上一首：prev")
    print("6. 停止：stop")
    print("7. 退出：exit")
    print("==========================\n")
    
    while True:
        command = input("请输入操作命令：").strip().lower()
        if command == "play":
            player.play_song()
        elif command == "pause":
            player.pause_song()
        elif command == "resume":
            player.resume_song()
        elif command == "next":
            player.next_song()
        elif command == "prev":
            player.prev_song()
        elif command == "stop":
            player.stop_song()
        elif command == "exit":
            player.stop_song()
            print("退出播放器")
            break
        else:
            print("无效命令，请重新输入！")