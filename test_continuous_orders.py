#!/usr/bin/env python3
"""
测试连续订单处理功能的脚本
"""

import subprocess
import time
import os

def test_continuous_orders():
    """测试连续订单处理功能"""
    print("🧪 开始测试连续订单处理功能")
    
    # 准备测试输入
    test_orders = [
        "西红柿炒蛋",
        "help", 
        "宫保鸡丁",
        "quit"
    ]
    
    # 创建输入字符串
    input_text = "\n".join(test_orders) + "\n"
    
    print(f"📝 测试订单序列: {test_orders}")
    print("🚀 启动主程序进行测试...")
    
    try:
        # 启动主程序并提供输入
        result = subprocess.run(
            ["python", "main.py"],
            input=input_text,
            text=True,
            capture_output=True,
            timeout=30  # 30秒超时
        )
        
        print("📊 测试输出:")
        print("=" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ 错误输出:")
            print(result.stderr)
        
        print("=" * 60)
        print(f"✅ 测试完成，返回码: {result.returncode}")
        
        # 检查是否包含预期的输出
        output = result.stdout
        success_indicators = [
            "连续订单处理模式",
            "已处理订单数量",
            "会话统计"
        ]
        
        passed_checks = 0
        for indicator in success_indicators:
            if indicator in output:
                passed_checks += 1
                print(f"✅ 发现预期输出: {indicator}")
            else:
                print(f"❌ 未发现预期输出: {indicator}")
        
        print(f"\n📈 测试通过率: {passed_checks}/{len(success_indicators)}")
        
        if passed_checks == len(success_indicators):
            print("🎉 连续订单处理功能测试通过！")
        else:
            print("⚠️ 部分功能可能存在问题")
            
    except subprocess.TimeoutExpired:
        print("⏰ 测试超时，可能程序在等待toio设备连接")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    test_continuous_orders()