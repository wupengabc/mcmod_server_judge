import glob
import os
import requests
import re
import zipfile
import toml
from bs4 import BeautifulSoup


# 获取当前目录所有jar文件
def get_jar():
    directory = "./"
    extension = "jar"
    pattern = f"{directory}/*.{extension}"
    files = glob.glob(pattern)
    return files


# 临时解压jar文件META-INF下的mods.toml文件
def unpack_jar(jar_name):
    jar_path = "./" + jar_name
    save_path = "./jar_unpack"
    try:
        zipfile.ZipFile(jar_path).extract("META-INF/mods.toml", save_path)
        return True
    except:
        return None


# 读取mods.toml的模组信息
def get_info():
    file_path = "./jar_unpack/META-INF/mods.toml"
    try:
        toml_content = toml.load(file_path)
        mod_info = toml_content["mods"][0]["modId"]
        return mod_info
    except:
        return None


# 删除临时文件
def remove_file():
    os.remove("./jar_unpack/META-INF/mods.toml")


# 通过在mods.toml中获取的mod信息在mc百科搜索该mod,并获取第一个搜索结果mod的介绍链接
def get_modurl(mod_info):
    search_url = "https://search.mcmod.cn/s?key=" + mod_info + "&filter=1&mold="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36'
    }
    search_result = requests.get(search_url, headers=headers)
    pattern = r'https://www.mcmod.cn/class/\d+.html'
    match = re.search(pattern, search_result.text)
    if match == None:
        return None
    else:
        return match.group()


# 使用bing的搜索搜索该mod在mc百科的内容
def get_bybing(modinfo):
    search_url = "https://www.bing.com/search?q=" + modinfo + "mc百科"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36'
    }
    content = requests.get(search_url, headers=headers)
    pattern = r'https://www.mcmod.cn/class/\d+.html'
    match = re.search(pattern, content.text)
    if match is None:
        return None
    else:
        return match.group()


# 解析mod介绍页面 获取介绍页面的mod名和运行环境
def get_state(mod_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36'
    }
    mod_info = requests.get(mod_url, headers=headers)
    pattern = r'运行环境:(.{13})'
    content = mod_info.text
    soup = BeautifulSoup(content, "lxml")
    title = soup.title.string
    match = re.search(pattern, content)
    if match is None:
        info = [title, '该模组暂无运行环境介绍']
        return info
    else:
        info = [title, match.group()]
        return info


# 创建一个文本文档储存内容
def mkdir():
    # 定义要创建的文件名
    filename = "state.txt"

    # 打开文件，以写入模式创建文件
    with open(filename, "w", encoding="utf-8") as file:
        # 写入 1000 行空白
        for _ in range(1000):
            file.write("\n")


# 将获取的内容写入文件夹
def write_to_line(file_path, line_number, content):
    # 读取文件内容
    with open(file_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()

    # 插入或替换指定行的内容
    if 1 <= line_number <= len(lines):
        lines[line_number - 1] = content + '\n'
    else:
        print(f"指定的行号超出范围")

    # 将修改后的内容写回文件
    with open(file_path, 'w', encoding="utf-8") as file:
        file.writelines(lines)


filenames = get_jar()
mkdir()
i = 0
for filename in filenames:
    i += 1
    unpack = unpack_jar(filename)
    if unpack is None:
        error = str(i) + filename + "  该mod内未含有mods.tomls文件,尝试使用文件名搜索"
        print(error)
        mod_url = get_modurl(filename)
        if mod_url is None:
            content = filename + '  使用mc百科搜索失败,尝试使用bing搜索'
            mod_url = get_bybing(filename)
            print(content)
            if mod_url is None:
                error = str(i) + filename + "使用bing搜索失败"
                write_to_line("./state.txt", i, error)
            else:
                info = get_state(mod_url)
                mod_state = str(i) + ".(文件名搜索(bing))模组名:" + info[0] + "  文件名:" + filename + "   " + info[
                    1] + "   模组链接:" + mod_url
                print(mod_state)
                write_to_line("./state.txt", i, mod_state)
        else:
            info = get_state(mod_url)
            mod_state = str(i) + ".(文件名搜索(百科搜索))模组名:" + info[0] + "  文件名:" + filename + "   " + info[
                1] + "   模组链接:" + mod_url
            print(mod_state)
            write_to_line("./state.txt", i, mod_state)
    else:
        mod_info = get_info()
        remove_file()
        if mod_info is None:
            error = str(i) + filename + "  的mods.toml文件读取失败,尝试使用文件名搜索"
            print(error)
            mod_url = get_modurl(filename)
            if mod_url is None:
                content = filename + '  使用mc百科搜索失败,尝试使用bing搜索'
                mod_url = get_bybing(filename)
                print(content)
                if mod_url is None:
                    error = str(i) + filename + "使用bing搜索失败"
                    write_to_line("./state.txt", i, error)
                else:
                    info = get_state(mod_url)
                    mod_state = str(i) + ".(文件名搜索(bing))模组名:" + info[0] + "  文件名:" + filename + "   " + info[
                        1] + "   模组链接:" + mod_url
                    print(mod_state)
                    write_to_line("./state.txt", i, mod_state)
            else:
                info = get_state(mod_url)
                mod_state = str(i) + ".(文件名搜索(百科搜索))模组名:" + info[0] + "  文件名:" + filename + "   " + info[
                    1] + "   模组链接:" + mod_url
                print(mod_state)
                write_to_line("./state.txt", i, mod_state)
        else:
            mod_url = get_modurl(mod_info)
            if mod_url is None:
                content = filename + '  使用mc百科搜索失败,尝试使用bing搜索'
                mod_url = get_bybing(mod_info)
                print(content)
                if mod_url is None:
                    error = str(i) + filename + "使用bing搜索失败"
                    write_to_line("./state.txt", i, error)
                else:
                    info = get_state(mod_url)
                    mod_state = str(i) + ".(bing)模组名:" + info[0] + "  文件名:" + filename + "   " + info[
                        1] + "   模组链接:" + mod_url
                    print(mod_state)
                    write_to_line("./state.txt", i, mod_state)
            else:
                info = get_state(mod_url)
                mod_state = str(i) + ".(百科搜索)模组名:" + info[0] + "  文件名:" + filename + "   " + info[
                    1] + "   模组链接:" + mod_url
                print(mod_state)
                write_to_line("./state.txt", i, mod_state)