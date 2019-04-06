import sys
sys.path.insert(0, '..')


''' 创建数据库 '''


if __name__ == '__main__':
    from models.base import create_all_tables

    create_all_tables()
