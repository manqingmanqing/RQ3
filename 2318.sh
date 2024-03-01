#!/bin/bash

# 无限循环
while true; do
    # 尝试运行1.py
    # python3 test2318.py
    # if [ $? -ne 0 ]; then
    #     echo "1.py failed, starting 2.py..."
    # else
    #     echo "1.py completed successfully, restarting it..."
    #     continue
    # fi

    # 如果1.py失败，则运行2.py
    python3 test2318.py
    if [ $? -ne 0 ]; then
        echo "2.py failed, starting 1.py..."
    else
        echo "2.py completed successfully, restarting it..."
    fi
done
