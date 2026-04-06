"""
GitHub API Push测试服务
提供HTTP API端点，用于测试GitHub API的push功能
"""

import os
import hashlib
from datetime import datetime
from flask import Flask, jsonify
from github import Github
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 从环境变量获取配置
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'main')


def generate_random_filename():
    """生成随机MD5字符串作为文件名"""
    timestamp = str(datetime.now().timestamp())
    md5_hash = hashlib.md5(timestamp.encode()).hexdigest()
    return f"{md5_hash}.txt"


def create_file_content():
    """创建文件内容，包含当前时间戳"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f"{current_time} - test push"


def push_to_github(filename, content):
    """在本地创建文件，然后通过GitHub API push到远程仓库"""
    try:
        # 获取当前项目目录
        repo_path = os.path.dirname(os.path.abspath(__file__))
        
        # 在本地创建文件
        file_path = os.path.join(repo_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 初始化GitHub客户端
        g = Github(GITHUB_TOKEN)
        
        # 获取仓库对象
        repo = g.get_repo(GITHUB_REPO)
        
        # 通过API创建文件并提交
        repo.create_file(
            path=filename,
            message=f"Add test file: {filename}",
            content=content,
            branch=GITHUB_BRANCH
        )
        
        return True, None
    except Exception as e:
        return False, str(e)


@app.route('/test', methods=['GET'])
def test_push():
    """
    测试push端点
    访问此端点会生成一个随机文件并push到GitHub仓库
    """
    # 生成随机文件名
    filename = generate_random_filename()
    
    # 创建文件内容
    content = create_file_content()
    
    # Push到GitHub
    success, error = push_to_github(filename, content)
    
    if success:
        return jsonify({
            "success": True,
            "filename": filename
        }), 200
    else:
        return jsonify({
            "success": False,
            "filename": filename,
            "error": error
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    # 检查环境变量是否配置
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("错误: 请配置环境变量 GITHUB_TOKEN 和 GITHUB_REPO")
        print("可以创建 .env 文件并设置:")
        print("GITHUB_TOKEN=your_personal_access_token")
        print("GITHUB_REPO=owner/repo")
        print("GITHUB_BRANCH=main")
        exit(1)
    
    # 启动Flask服务
    app.run(host='0.0.0.0', port=5000, debug=True)
