import json

from equipment_tools import get_equipment_parameter


def main():
    model = input("请输入设备型号：")
    field = input("请输入参数名称：")

    result = get_equipment_parameter(model, field)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()