from data.cases import get_cases

cases = get_cases()
print(f"成功加载案例数: {len(cases)}")
print("\n案例列表:")
for i, case in enumerate(cases, 1):
    print(f"{i}. {case['id']}: {case['title']}")
