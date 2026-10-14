# ==========================================
# 역화살표 표기법
# Reverse Arrow Notation - GMP Edition
# ==========================================

import gmpy2
import time
import sys

from gmpy2 import mpz

# ==========================================
# 설정
# ==========================================

# 계산 결과 하나당 허용할 최대 비트 수
# 메모리 상황에 맞게 조절 가능
MAX_BITS = 10_000_000

# 화면에 출력할 최대 자릿수
MAX_DISPLAY_DIGITS = 3000

# 큰 정수 문자열 변환 제한 해제
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


# ==========================================
# 안전한 초거대수 거듭제곱
# ==========================================

class NumberTooLarge(Exception):
    pass


def huge_pow(base, exponent):
    base = mpz(base)
    exponent = mpz(exponent)

    if exponent < 0:
        raise ValueError("음수 지수는 지원하지 않아.")

    # 특별한 경우
    if exponent == 0:
        return mpz(1)

    if base == 0:
        return mpz(0)

    if base == 1:
        return mpz(1)

    # 결과의 비트 크기를 보수적으로 추정
    # base >= 2일 때 실제 비트 수는
    # exponent * base.bit_length() 이하
    base_bits = base.bit_length()

    if exponent > MAX_BITS // base_bits:
        raise NumberTooLarge(
            "거듭제곱 결과가 설정된 비트 제한을 "
            "초과할 가능성이 있어."
        )

    # GMP 기반 정확한 정수 거듭제곱
    return base ** exponent


# ==========================================
# 역화살표 계산 엔진
# ==========================================

def reverse_arrow(expression):

    # 입력 처리
    try:
        X = [
            mpz(x.strip())
            for x in expression.split("<-")
        ]

    except (ValueError, TypeError):
        raise ValueError(
            "입력 형식 오류! 예: 2 <- 2 <- 2"
        )

    if len(X) < 2:
        raise ValueError(
            "최소 2개의 숫자를 입력해야 해."
        )

    if any(x < 1 for x in X):
        raise ValueError(
            "1 이상의 정수만 사용할 수 있어."
        )

    n = len(X)

    # ======================================
    # STEP 1
    # 오른쪽부터 거듭제곱 계산
    # ======================================

    x_r = [mpz(0)] * n
    x_r[-1] = X[-1]

    for i in range(n - 2, -1, -1):

        x_r[i] = huge_pow(
            X[i],
            x_r[i + 1]
        )

    # ======================================
    # STEP 2
    # 2로 나눈 후 올림
    # ======================================

    x_d = [
        (value + 1) // 2
        for value in x_r
    ]

    # ======================================
    # STEP 3
    # 두 번째 거듭제곱 탑
    # ======================================

    r_xd = x_d[-1]

    for i in range(n - 2, -1, -1):

        r_xd = huge_pow(
            x_d[i],
            r_xd
        )

    # ======================================
    # STEP 4
    # 최종 결과
    # ======================================

    r_xr = x_r[0]

    final_result = r_xr + r_xd

    if final_result.bit_length() > MAX_BITS:
        raise NumberTooLarge(
            "최종 결과가 비트 제한을 초과했어."
        )

    return {
        "X": X,
        "x_result": x_r,
        "x_divide": x_d,
        "R(x_r)": r_xr,
        "R(x_d)": r_xd,
        "Result": final_result
    }


# ==========================================
# 숫자 출력 시스템
# ==========================================

def display_number(value):

    if isinstance(value, list):
        return "[" + ", ".join(
            display_number(v) for v in value
        ) + "]"

    value = mpz(value)

    # 빠른 자릿수 추정
    # gmpy2.num_digits()는 1자리 크게 나올 수 있음
    estimated_digits = value.num_digits(10)

    if estimated_digits > MAX_DISPLAY_DIGITS + 1:

        return (
            f"<초거대 정수 | "
            f"약 {estimated_digits:,}자리 | "
            f"{value.bit_length():,}비트>"
        )

    # 작은 수는 정확하게 출력
    return str(value)


# ==========================================
# 메인 프로그램
# ==========================================

def main():

    print("=" * 55)
    print("           역화살표 표기법 - GMP Edition")
    print("=" * 55)

    print("\n입력 예시: 2 <- 2 <- 2")
    print("종료하려면 exit 입력\n")

    while True:

        expression = input("Reverse Arrow > ").strip()

        if expression.lower() in ("exit", "quit"):
            print("\n프로그램 종료!")
            break

        start = time.perf_counter()

        try:

            result = reverse_arrow(expression)

            elapsed = time.perf_counter() - start

            print("\n" + "=" * 55)
            print("계산 결과")
            print("=" * 55)

            for key, value in result.items():

                print(
                    f"\n{key}: "
                    f"{display_number(value)}"
                )

            final = result["Result"]

            print("\n" + "=" * 55)
            print("계산 통계")
            print("=" * 55)

            print(
                f"계산 시간: {elapsed:.6f}초"
            )

            print(
                f"비트 수: {final.bit_length():,}"
            )

            print(
                f"자릿수 추정: "
                f"{final.num_digits(10):,}"
            )

            print(
                f"GMP 버전: {gmpy2.mp_version()}"
            )

            print(
                "정수 연산: 정확한 계산"
            )

        except NumberTooLarge as e:

            print("\n[계산 크기 제한]")
            print(e)

            print(
                "MAX_BITS를 높이면 더 큰 수를 "
                "계산할 수 있지만 메모리 사용량도 늘어나."
            )

        except (ValueError, OverflowError, MemoryError) as e:

            print("\n[계산 오류]")
            print(e)

        except KeyboardInterrupt:

            print("\n계산 중단!")
            break

        print()


if __name__ == "__main__":
    main()