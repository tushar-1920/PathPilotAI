"""
PathPilot AI — Battle Mode Service
Manages 1v1 coding duels with AI-generated problems, live judging, XP, trophies, badges.
"""

import random
import time
from datetime import datetime

# ── In-memory duel rooms (like VidCode rooms) ─────────────────────────────────
_duels = {}   # duel_code -> duel dict

# ── XP Constants (per battle) ─────────────────────────────────────────────────
XP_WIN_EASY   = 50
XP_WIN_MEDIUM = 100
XP_WIN_HARD   = 200
XP_LOSE_EASY  = 10
XP_LOSE_MEDIUM= 20
XP_LOSE_HARD  = 35
XP_DRAW       = 25

# ── Trophy Constants (per battle) ─────────────────────────────────────────────
TROPHY_WIN_EASY   = 15
TROPHY_WIN_MEDIUM = 20
TROPHY_WIN_HARD   = 30
TROPHY_LOSE_EASY  = -3
TROPHY_LOSE_MEDIUM= -4
TROPHY_LOSE_HARD  = -5
TROPHY_DRAW       = 0

# ── League System (based on trophy count) ─────────────────────────────────────
# Each league has 3 tiers. Trophies go up on win, down on loss.
LEAGUES = [
    # (min_trophies, name, tier, icon, color, badge_color)
    (0,     "Wood",    "I",   "🪵", "#8B4513", "rgba(139,69,19,.3)"),
    (50,    "Wood",    "II",  "🪵", "#8B4513", "rgba(139,69,19,.3)"),
    (100,   "Wood",    "III", "🪵", "#8B4513", "rgba(139,69,19,.3)"),
    (175,   "Bronze",  "I",   "🥉", "#cd7f32", "rgba(205,127,50,.3)"),
    (250,   "Bronze",  "II",  "🥉", "#cd7f32", "rgba(205,127,50,.3)"),
    (350,   "Bronze",  "III", "🥉", "#cd7f32", "rgba(205,127,50,.3)"),
    (475,   "Silver",  "I",   "🥈", "#c0c0c0", "rgba(192,192,192,.3)"),
    (625,   "Silver",  "II",  "🥈", "#c0c0c0", "rgba(192,192,192,.3)"),
    (800,   "Silver",  "III", "🥈", "#c0c0c0", "rgba(192,192,192,.3)"),
    (1000,  "Gold",    "I",   "🥇", "#ffd700", "rgba(255,215,0,.3)"),
    (1250,  "Gold",    "II",  "🥇", "#ffd700", "rgba(255,215,0,.3)"),
    (1550,  "Gold",    "III", "🥇", "#ffd700", "rgba(255,215,0,.3)"),
    (1900,  "Platinum","I",   "🔷", "#e5e4e2", "rgba(229,228,226,.3)"),
    (2300,  "Platinum","II",  "🔷", "#e5e4e2", "rgba(229,228,226,.3)"),
    (2750,  "Platinum","III", "🔷", "#e5e4e2", "rgba(229,228,226,.3)"),
    (3250,  "Diamond", "I",   "💎", "#00e5c8", "rgba(0,229,200,.3)"),
    (3800,  "Diamond", "II",  "💎", "#00e5c8", "rgba(0,229,200,.3)"),
    (4400,  "Diamond", "III", "💎", "#00e5c8", "rgba(0,229,200,.3)"),
    (5100,  "Master",  "I",   "🌟", "#a855f7", "rgba(168,85,247,.3)"),
    (5900,  "Master",  "II",  "🌟", "#a855f7", "rgba(168,85,247,.3)"),
    (6800,  "Master",  "III", "🌟", "#a855f7", "rgba(168,85,247,.3)"),
    (7800,  "Grandmaster","I","👑", "#ff5757", "rgba(255,87,87,.3)"),
    (9000,  "Grandmaster","II","👑","#ff5757", "rgba(255,87,87,.3)"),
    (10500, "Grandmaster","III","👑","#ff5757","rgba(255,87,87,.3)"),
    (12000, "Legend",   "",   "🔥", "linear-gradient(135deg,#ff5757,#ffb547)", "rgba(255,87,87,.3)"),
]

# ── XP Thresholds (separate from trophies) ────────────────────────────────────
XP_RANKS = [
    (0,     "Newbie",      "⚪", "rgba(255,255,255,.15)"),
    (100,   "Beginner",    "🟤", "rgba(139,69,19,.4)"),
    (300,   "Learner",     "🟢", "rgba(34,197,94,.4)"),
    (600,   "Coder",       "🔵", "rgba(56,189,248,.4)"),
    (1000,  "Developer",   "🟣", "rgba(168,85,247,.4)"),
    (1700,  "Engineer",    "🟡", "rgba(255,215,0,.4)"),
    (2700,  "Expert",      "🟠", "rgba(255,140,0,.4)"),
    (4000,  "Elite",       "🔴", "rgba(255,87,87,.4)"),
    (6000,  "Master Coder","💜", "rgba(168,85,247,.5)"),
    (10000, "Code God",    "⚡", "rgba(0,229,200,.5)"),
]

# ── Battle Mode Problem Bank (100+ problems across difficulties) ───────────────
BATTLE_PROBLEMS = {
    "easy": [
        {
            "id": "b1", "title": "Two Sum",
            "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
            "examples": [
                {"input": "nums = [2,7,11,15], target = 9", "output": "[0, 1]", "explanation": "nums[0] + nums[1] = 2 + 7 = 9"},
                {"input": "nums = [3,2,4], target = 6", "output": "[1, 2]", "explanation": "nums[1] + nums[2] = 2 + 4 = 6"},
            ],
            "constraints": ["2 ≤ nums.length ≤ 10⁴", "-10⁹ ≤ nums[i] ≤ 10⁹", "Only one valid answer exists."],
            "test_cases": [{"input": "[2,7,11,15]\n9", "expected": "[0, 1]"}, {"input": "[3,2,4]\n6", "expected": "[1, 2]"}, {"input": "[3,3]\n6", "expected": "[0, 1]"}],
            "tags": ["Array", "Hash Table"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "def two_sum(nums, target):\n    # Write your solution here\n    pass\n\nimport json\nnums = json.loads(input())\ntarget = int(input())\nprint(two_sum(nums, target))", "javascript": "const readline = require('readline');\nconst rl = readline.createInterface({ input: process.stdin });\nlet lines = [];\nrl.on('line', l => lines.push(l));\nrl.on('close', () => {\n  const nums = JSON.parse(lines[0]);\n  const target = parseInt(lines[1]);\n  // Write your solution here\n  function twoSum(nums, target) { }\n  console.log(JSON.stringify(twoSum(nums, target)));\n});"}
        },
        {
            "id": "b2", "title": "Palindrome Check",
            "description": "Given a string s, return true if it is a palindrome, or false otherwise. A phrase is a palindrome if, after converting all uppercase letters to lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward.",
            "examples": [
                {"input": "s = \"A man, a plan, a canal: Panama\"", "output": "true", "explanation": "After filtering: 'amanaplanacanalpanama'"},
                {"input": "s = \"race a car\"", "output": "false", "explanation": "After filtering: 'raceacar'"},
            ],
            "constraints": ["1 ≤ s.length ≤ 2*10⁵", "s consists only of printable ASCII characters."],
            "test_cases": [{"input": "\"A man, a plan, a canal: Panama\"", "expected": "true"}, {"input": "\"race a car\"", "expected": "false"}, {"input": "\" \"", "expected": "true"}],
            "tags": ["String", "Two Pointers"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "s = input().strip('\"')\n# Write your solution here\ndef is_palindrome(s):\n    pass\nprint('true' if is_palindrome(s) else 'false')", "javascript": "const s = require('fs').readFileSync('/dev/stdin','utf8').trim().replace(/^\"|\"$/g,'');\nfunction isPalindrome(s) { }\nconsole.log(isPalindrome(s) ? 'true' : 'false');"}
        },
        {
            "id": "b3", "title": "Reverse a String",
            "description": "Write a function that reverses a string. The input string is given as an array of characters s. You must do this by modifying the input array in-place with O(1) extra memory.",
            "examples": [
                {"input": "s = [\"h\",\"e\",\"l\",\"l\",\"o\"]", "output": "[\"o\",\"l\",\"l\",\"e\",\"h\"]", "explanation": "Reverse the array in-place"},
                {"input": "s = [\"H\",\"a\",\"n\",\"n\",\"a\",\"h\"]", "output": "[\"h\",\"a\",\"n\",\"n\",\"a\",\"H\"]", "explanation": ""},
            ],
            "constraints": ["1 ≤ s.length ≤ 10⁵"],
            "test_cases": [{"input": "[\"h\",\"e\",\"l\",\"l\",\"o\"]", "expected": "[\"o\", \"l\", \"l\", \"e\", \"h\"]"}, {"input": "[\"H\",\"a\",\"n\",\"n\",\"a\",\"h\"]", "expected": "[\"h\", \"a\", \"n\", \"n\", \"a\", \"H\"]"}],
            "tags": ["String", "Two Pointers"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "import json\ns = json.loads(input())\n# Reverse in-place\ndef reverse_string(s):\n    pass\nreverse_string(s)\nprint(json.dumps(s))", "javascript": "const s = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction reverseString(s) { }\nreverseString(s);\nconsole.log(JSON.stringify(s));"}
        },
        {
            "id": "b4", "title": "FizzBuzz",
            "description": "Given an integer n, return a string array answer where: answer[i] == \"FizzBuzz\" if i is divisible by 3 and 5, answer[i] == \"Fizz\" if i is divisible by 3, answer[i] == \"Buzz\" if i is divisible by 5, answer[i] == i (as a string) otherwise.",
            "examples": [
                {"input": "n = 3", "output": "[\"1\",\"2\",\"Fizz\"]", "explanation": ""},
                {"input": "n = 5", "output": "[\"1\",\"2\",\"Fizz\",\"4\",\"Buzz\"]", "explanation": ""},
            ],
            "constraints": ["1 ≤ n ≤ 10⁴"],
            "test_cases": [{"input": "3", "expected": "['1', '2', 'Fizz']"}, {"input": "5", "expected": "['1', '2', 'Fizz', '4', 'Buzz']"}, {"input": "15", "expected": "['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']"}],
            "tags": ["Math", "String", "Simulation"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "n = int(input())\ndef fizz_buzz(n):\n    # Write your solution here\n    pass\nprint(fizz_buzz(n))", "javascript": "const n = parseInt(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction fizzBuzz(n) { }\nconsole.log(JSON.stringify(fizzBuzz(n)));"}
        },
        {
            "id": "b5", "title": "Maximum Subarray",
            "description": "Given an integer array nums, find the subarray with the largest sum, and return its sum.",
            "examples": [
                {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6", "explanation": "The subarray [4,-1,2,1] has the largest sum = 6."},
                {"input": "nums = [1]", "output": "1", "explanation": ""},
            ],
            "constraints": ["1 ≤ nums.length ≤ 10⁵", "-10⁴ ≤ nums[i] ≤ 10⁴"],
            "test_cases": [{"input": "[-2,1,-3,4,-1,2,1,-5,4]", "expected": "6"}, {"input": "[1]", "expected": "1"}, {"input": "[5,4,-1,7,8]", "expected": "23"}],
            "tags": ["Array", "Dynamic Programming", "Divide and Conquer"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "import json\nnums = json.loads(input())\ndef max_subarray(nums):\n    # Write your solution here\n    pass\nprint(max_subarray(nums))", "javascript": "const nums = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction maxSubArray(nums) { }\nconsole.log(maxSubArray(nums));"}
        },
        {
            "id": "b6", "title": "Count Vowels",
            "description": "Given a string s, return the number of vowels (a, e, i, o, u) in it. Consider both uppercase and lowercase vowels.",
            "examples": [
                {"input": "s = \"Hello World\"", "output": "3", "explanation": "e, o, o are vowels"},
                {"input": "s = \"AEIOU\"", "output": "5", "explanation": "All are vowels"},
            ],
            "constraints": ["1 ≤ s.length ≤ 10⁵"],
            "test_cases": [{"input": "Hello World", "expected": "3"}, {"input": "AEIOU", "expected": "5"}, {"input": "xyz", "expected": "0"}],
            "tags": ["String"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "s = input()\ndef count_vowels(s):\n    # Write your solution here\n    pass\nprint(count_vowels(s))", "javascript": "const s = require('fs').readFileSync('/dev/stdin','utf8').trim();\nfunction countVowels(s) { }\nconsole.log(countVowels(s));"}
        },
        {
            "id": "b7", "title": "Single Number",
            "description": "Given a non-empty array of integers nums, every element appears twice except for one. Find that single one. You must implement a solution with linear runtime complexity and use only constant extra space.",
            "examples": [
                {"input": "nums = [2,2,1]", "output": "1", "explanation": ""},
                {"input": "nums = [4,1,2,1,2]", "output": "4", "explanation": ""},
            ],
            "constraints": ["1 ≤ nums.length ≤ 3*10⁴"],
            "test_cases": [{"input": "[2,2,1]", "expected": "1"}, {"input": "[4,1,2,1,2]", "expected": "4"}, {"input": "[1]", "expected": "1"}],
            "tags": ["Array", "Bit Manipulation"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "import json\nnums = json.loads(input())\ndef single_number(nums):\n    # Write your solution here\n    pass\nprint(single_number(nums))", "javascript": "const nums = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction singleNumber(nums) { }\nconsole.log(singleNumber(nums));"}
        },
        {
            "id": "b8", "title": "Fibonacci Number",
            "description": "The Fibonacci numbers form a sequence, where each number is the sum of the two preceding ones, starting from 0 and 1. Given n, calculate F(n).",
            "examples": [
                {"input": "n = 2", "output": "1", "explanation": "F(2) = F(1) + F(0) = 1 + 0 = 1"},
                {"input": "n = 4", "output": "3", "explanation": "F(4) = F(3) + F(2) = 2 + 1 = 3"},
            ],
            "constraints": ["0 ≤ n ≤ 30"],
            "test_cases": [{"input": "2", "expected": "1"}, {"input": "4", "expected": "3"}, {"input": "10", "expected": "55"}],
            "tags": ["Math", "Dynamic Programming", "Recursion"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "n = int(input())\ndef fib(n):\n    # Write your solution here\n    pass\nprint(fib(n))", "javascript": "const n = parseInt(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction fib(n) { }\nconsole.log(fib(n));"}
        },
        {
            "id": "b9", "title": "Missing Number",
            "description": "Given an array nums containing n distinct numbers in the range [0, n], return the only number in the range that is missing from the array.",
            "examples": [
                {"input": "nums = [3,0,1]", "output": "2", "explanation": "n = 3, so numbers are 0,1,2,3. Missing is 2."},
                {"input": "nums = [0,1]", "output": "2", "explanation": ""},
            ],
            "constraints": ["n == nums.length", "1 ≤ n ≤ 10⁴"],
            "test_cases": [{"input": "[3,0,1]", "expected": "2"}, {"input": "[0,1]", "expected": "2"}, {"input": "[9,6,4,2,3,5,7,0,1]", "expected": "8"}],
            "tags": ["Array", "Math", "Bit Manipulation"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "import json\nnums = json.loads(input())\ndef missing_number(nums):\n    # Write your solution here\n    pass\nprint(missing_number(nums))", "javascript": "const nums = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction missingNumber(nums) { }\nconsole.log(missingNumber(nums));"}
        },
        {
            "id": "b10", "title": "Power of Two",
            "description": "Given an integer n, return true if it is a power of two. Otherwise, return false. An integer n is a power of two if there exists an integer x such that n == 2^x.",
            "examples": [
                {"input": "n = 1", "output": "true", "explanation": "2^0 = 1"},
                {"input": "n = 16", "output": "true", "explanation": "2^4 = 16"},
                {"input": "n = 3", "output": "false", "explanation": ""},
            ],
            "constraints": ["-2³¹ ≤ n ≤ 2³¹ - 1"],
            "test_cases": [{"input": "1", "expected": "true"}, {"input": "16", "expected": "true"}, {"input": "3", "expected": "false"}],
            "tags": ["Math", "Bit Manipulation", "Recursion"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "n = int(input())\ndef is_power_of_two(n):\n    # Write your solution here\n    pass\nprint('true' if is_power_of_two(n) else 'false')", "javascript": "const n = parseInt(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction isPowerOfTwo(n) { }\nconsole.log(isPowerOfTwo(n) ? 'true' : 'false');"}
        },
        {
            "id": "b11", "title": "Reverse Integer",
            "description": "Given a signed 32-bit integer x, return x with its digits reversed. If reversing x causes the value to go outside the signed 32-bit integer range [-2³¹, 2³¹ - 1], return 0.",
            "examples": [
                {"input": "x = 123", "output": "321", "explanation": ""},
                {"input": "x = -123", "output": "-321", "explanation": ""},
                {"input": "x = 120", "output": "21", "explanation": ""},
            ],
            "constraints": ["-2³¹ ≤ x ≤ 2³¹ - 1"],
            "test_cases": [{"input": "123", "expected": "321"}, {"input": "-123", "expected": "-321"}, {"input": "120", "expected": "21"}],
            "tags": ["Math"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "x = int(input())\ndef reverse(x):\n    # Write your solution here\n    pass\nprint(reverse(x))", "javascript": "const x = parseInt(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction reverse(x) { }\nconsole.log(reverse(x));"}
        },
        {
            "id": "b12", "title": "Sqrt(x)",
            "description": "Given a non-negative integer x, return the square root of x rounded down to the nearest integer. The returned integer should be non-negative as well. You must not use any built-in exponent function or operator.",
            "examples": [
                {"input": "x = 4", "output": "2", "explanation": ""},
                {"input": "x = 8", "output": "2", "explanation": "sqrt(8) ≈ 2.828..., rounded down = 2"},
            ],
            "constraints": ["0 ≤ x ≤ 2³¹ - 1"],
            "test_cases": [{"input": "4", "expected": "2"}, {"input": "8", "expected": "2"}, {"input": "0", "expected": "0"}],
            "tags": ["Math", "Binary Search"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "x = int(input())\ndef my_sqrt(x):\n    # Write your solution here (no math.sqrt!)\n    pass\nprint(my_sqrt(x))", "javascript": "const x = parseInt(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction mySqrt(x) { }\nconsole.log(mySqrt(x));"}
        },
        {
            "id": "b13", "title": "Count Bits",
            "description": "Given an integer n, return an array ans of length n + 1 such that for each i (0 ≤ i ≤ n), ans[i] is the number of 1's in the binary representation of i.",
            "examples": [
                {"input": "n = 2", "output": "[0,1,1]", "explanation": "0→0 ones, 1→1 one, 2→1 one"},
                {"input": "n = 5", "output": "[0,1,1,2,1,2]", "explanation": ""},
            ],
            "constraints": ["0 ≤ n ≤ 10⁵"],
            "test_cases": [{"input": "2", "expected": "[0, 1, 1]"}, {"input": "5", "expected": "[0, 1, 1, 2, 1, 2]"}],
            "tags": ["Dynamic Programming", "Bit Manipulation"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "n = int(input())\ndef count_bits(n):\n    # Write your solution here\n    pass\nprint(count_bits(n))", "javascript": "const n = parseInt(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction countBits(n) { }\nconsole.log(JSON.stringify(countBits(n)));"}
        },
        {
            "id": "b14", "title": "Find Maximum in Array",
            "description": "Given an array of integers, find and return the maximum element.",
            "examples": [
                {"input": "nums = [3,1,4,1,5,9,2,6]", "output": "9", "explanation": "9 is the largest element"},
                {"input": "nums = [-1,-5,-3]", "output": "-1", "explanation": "-1 is the largest among negatives"},
            ],
            "constraints": ["1 ≤ nums.length ≤ 10⁵"],
            "test_cases": [{"input": "[3,1,4,1,5,9,2,6]", "expected": "9"}, {"input": "[-1,-5,-3]", "expected": "-1"}, {"input": "[1]", "expected": "1"}],
            "tags": ["Array"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "import json\nnums = json.loads(input())\ndef find_max(nums):\n    pass\nprint(find_max(nums))", "javascript": "const nums = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction findMax(nums) { }\nconsole.log(findMax(nums));"}
        },
        {
            "id": "b15", "title": "Sum of Digits",
            "description": "Given a non-negative integer n, return the sum of its digits.",
            "examples": [
                {"input": "n = 123", "output": "6", "explanation": "1+2+3=6"},
                {"input": "n = 9", "output": "9", "explanation": ""},
            ],
            "constraints": ["0 ≤ n ≤ 10⁹"],
            "test_cases": [{"input": "123", "expected": "6"}, {"input": "9", "expected": "9"}, {"input": "1000", "expected": "1"}],
            "tags": ["Math"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "n = int(input())\ndef sum_digits(n):\n    pass\nprint(sum_digits(n))", "javascript": "const n = parseInt(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction sumDigits(n) { }\nconsole.log(sumDigits(n));"}
        },
        {
            "id": "b16", "title": "Is Anagram",
            "description": "Given two strings s and t, return true if t is an anagram of s, and false otherwise.",
            "examples": [
                {"input": "s = \"anagram\", t = \"nagaram\"", "output": "true", "explanation": ""},
                {"input": "s = \"rat\", t = \"car\"", "output": "false", "explanation": ""},
            ],
            "constraints": ["1 ≤ s.length, t.length ≤ 5*10⁴"],
            "test_cases": [{"input": "anagram\nnagaram", "expected": "true"}, {"input": "rat\ncar", "expected": "false"}],
            "tags": ["Hash Table", "String", "Sorting"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "s = input()\nt = input()\ndef is_anagram(s, t):\n    pass\nprint('true' if is_anagram(s, t) else 'false')", "javascript": "const lines = require('fs').readFileSync('/dev/stdin','utf8').trim().split('\\n');\nfunction isAnagram(s, t) { }\nconsole.log(isAnagram(lines[0], lines[1]) ? 'true' : 'false');"}
        },
        {
            "id": "b17", "title": "Pascal's Triangle Row",
            "description": "Given an integer rowIndex, return the rowIndex-th (0-indexed) row of Pascal's triangle.",
            "examples": [
                {"input": "rowIndex = 3", "output": "[1,3,3,1]", "explanation": ""},
                {"input": "rowIndex = 0", "output": "[1]", "explanation": ""},
            ],
            "constraints": ["0 ≤ rowIndex ≤ 33"],
            "test_cases": [{"input": "3", "expected": "[1, 3, 3, 1]"}, {"input": "0", "expected": "[1]"}, {"input": "4", "expected": "[1, 4, 6, 4, 1]"}],
            "tags": ["Array", "Dynamic Programming"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "row = int(input())\ndef get_row(rowIndex):\n    pass\nprint(get_row(row))", "javascript": "const row = parseInt(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction getRow(rowIndex) { }\nconsole.log(JSON.stringify(getRow(row)));"}
        },
        {
            "id": "b18", "title": "First Unique Character",
            "description": "Given a string s, find the first non-repeating character in it and return its index. If it does not exist, return -1.",
            "examples": [
                {"input": "s = \"leetcode\"", "output": "0", "explanation": "l appears only once, at index 0"},
                {"input": "s = \"aabb\"", "output": "-1", "explanation": ""},
            ],
            "constraints": ["1 ≤ s.length ≤ 10⁵", "s consists of only lowercase English letters."],
            "test_cases": [{"input": "leetcode", "expected": "0"}, {"input": "loveleetcode", "expected": "2"}, {"input": "aabb", "expected": "-1"}],
            "tags": ["Hash Table", "String", "Queue"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "s = input()\ndef first_uniq_char(s):\n    pass\nprint(first_uniq_char(s))", "javascript": "const s = require('fs').readFileSync('/dev/stdin','utf8').trim();\nfunction firstUniqChar(s) { }\nconsole.log(firstUniqChar(s));"}
        },
        {
            "id": "b19", "title": "Remove Duplicates from Sorted Array",
            "description": "Given an integer array nums sorted in non-decreasing order, remove the duplicates in-place such that each unique element appears only once. Return k after placing the final result in the first k slots of nums.",
            "examples": [
                {"input": "nums = [1,1,2]", "output": "2", "explanation": "k=2, first 2 elements are [1,2]"},
                {"input": "nums = [0,0,1,1,1,2,2,3,3,4]", "output": "5", "explanation": "k=5, first 5 are [0,1,2,3,4]"},
            ],
            "constraints": ["1 ≤ nums.length ≤ 3*10⁴"],
            "test_cases": [{"input": "[1,1,2]", "expected": "2"}, {"input": "[0,0,1,1,1,2,2,3,3,4]", "expected": "5"}],
            "tags": ["Array", "Two Pointers"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "import json\nnums = json.loads(input())\ndef remove_duplicates(nums):\n    pass\nprint(remove_duplicates(nums))", "javascript": "const nums = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction removeDuplicates(nums) { }\nconsole.log(removeDuplicates(nums));"}
        },
        {
            "id": "b20", "title": "Balanced Brackets",
            "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid (all brackets are properly closed and nested).",
            "examples": [
                {"input": "s = \"()\"", "output": "true", "explanation": ""},
                {"input": "s = \"()[]{}\"", "output": "true", "explanation": ""},
                {"input": "s = \"(]\"", "output": "false", "explanation": ""},
            ],
            "constraints": ["1 ≤ s.length ≤ 10⁴"],
            "test_cases": [{"input": "()", "expected": "true"}, {"input": "()[]{}", "expected": "true"}, {"input": "(]", "expected": "false"}, {"input": "([)]", "expected": "false"}],
            "tags": ["String", "Stack"], "difficulty": "easy", "time_limit": 10,
            "boilerplate": {"python": "s = input()\ndef is_valid(s):\n    pass\nprint('true' if is_valid(s) else 'false')", "javascript": "const s = require('fs').readFileSync('/dev/stdin','utf8').trim();\nfunction isValid(s) { }\nconsole.log(isValid(s) ? 'true' : 'false');"}
        },
    ],
    "medium": [
        {
            "id": "bm1", "title": "Longest Substring Without Repeating Characters",
            "description": "Given a string s, find the length of the longest substring without repeating characters.",
            "examples": [
                {"input": "s = \"abcabcbb\"", "output": "3", "explanation": "The answer is 'abc', with length 3."},
                {"input": "s = \"bbbbb\"", "output": "1", "explanation": "The answer is 'b', with length 1."},
            ],
            "constraints": ["0 ≤ s.length ≤ 5*10⁴"],
            "test_cases": [{"input": "abcabcbb", "expected": "3"}, {"input": "bbbbb", "expected": "1"}, {"input": "pwwkew", "expected": "3"}],
            "tags": ["Hash Table", "String", "Sliding Window"], "difficulty": "medium", "time_limit": 15,
            "boilerplate": {"python": "s = input()\ndef length_of_longest_substring(s):\n    pass\nprint(length_of_longest_substring(s))", "javascript": "const s = require('fs').readFileSync('/dev/stdin','utf8').trim();\nfunction lengthOfLongestSubstring(s) { }\nconsole.log(lengthOfLongestSubstring(s));"}
        },
        {
            "id": "bm2", "title": "3Sum",
            "description": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, j != k, and nums[i] + nums[j] + nums[k] == 0. The solution set must not contain duplicate triplets.",
            "examples": [
                {"input": "nums = [-1,0,1,2,-1,-4]", "output": "[[-1,-1,2],[-1,0,1]]", "explanation": ""},
                {"input": "nums = [0,1,1]", "output": "[]", "explanation": ""},
            ],
            "constraints": ["3 ≤ nums.length ≤ 3000", "-10⁵ ≤ nums[i] ≤ 10⁵"],
            "test_cases": [{"input": "[-1,0,1,2,-1,-4]", "expected": "[[-1, -1, 2], [-1, 0, 1]]"}, {"input": "[0,0,0]", "expected": "[[0, 0, 0]]"}],
            "tags": ["Array", "Two Pointers", "Sorting"], "difficulty": "medium", "time_limit": 15,
            "boilerplate": {"python": "import json\nnums = json.loads(input())\ndef three_sum(nums):\n    pass\nprint(three_sum(nums))", "javascript": "const nums = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction threeSum(nums) { }\nconsole.log(JSON.stringify(threeSum(nums)));"}
        },
        {
            "id": "bm3", "title": "Product of Array Except Self",
            "description": "Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i]. You must write an algorithm that runs in O(n) time and without using the division operation.",
            "examples": [
                {"input": "nums = [1,2,3,4]", "output": "[24,12,8,6]", "explanation": ""},
                {"input": "nums = [-1,1,0,-3,3]", "output": "[0,0,9,0,0]", "explanation": ""},
            ],
            "constraints": ["2 ≤ nums.length ≤ 10⁵"],
            "test_cases": [{"input": "[1,2,3,4]", "expected": "[24, 12, 8, 6]"}, {"input": "[-1,1,0,-3,3]", "expected": "[0, 0, 9, 0, 0]"}],
            "tags": ["Array", "Prefix Sum"], "difficulty": "medium", "time_limit": 15,
            "boilerplate": {"python": "import json\nnums = json.loads(input())\ndef product_except_self(nums):\n    pass\nprint(product_except_self(nums))", "javascript": "const nums = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction productExceptSelf(nums) { }\nconsole.log(JSON.stringify(productExceptSelf(nums)));"}
        },
        {
            "id": "bm4", "title": "Group Anagrams",
            "description": "Given an array of strings strs, group the anagrams together. You can return the answer in any order.",
            "examples": [
                {"input": "strs = [\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]", "output": "[[\"bat\"],[\"nat\",\"tan\"],[\"ate\",\"eat\",\"tea\"]]", "explanation": ""},
            ],
            "constraints": ["1 ≤ strs.length ≤ 10⁴"],
            "test_cases": [{"input": "[\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]", "expected": "3 groups"}, {"input": "[\"\"]", "expected": "[[\"\"]]"}],
            "tags": ["Array", "Hash Table", "String", "Sorting"], "difficulty": "medium", "time_limit": 15,
            "boilerplate": {"python": "import json\nstrs = json.loads(input())\ndef group_anagrams(strs):\n    pass\nresult = group_anagrams(strs)\nprint(len(result))  # number of groups", "javascript": "const strs = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction groupAnagrams(strs) { }\nconsole.log(groupAnagrams(strs).length);"}
        },
        {
            "id": "bm5", "title": "Container With Most Water",
            "description": "You are given an integer array height of length n. There are n vertical lines drawn. Find two lines that together with the x-axis form a container, such that the container contains the most water. Return the maximum amount of water a container can store.",
            "examples": [
                {"input": "height = [1,8,6,2,5,4,8,3,7]", "output": "49", "explanation": "The maximum is obtained using lines at index 1 and 8."},
                {"input": "height = [1,1]", "output": "1", "explanation": ""},
            ],
            "constraints": ["n == height.length", "2 ≤ n ≤ 10⁵"],
            "test_cases": [{"input": "[1,8,6,2,5,4,8,3,7]", "expected": "49"}, {"input": "[1,1]", "expected": "1"}],
            "tags": ["Array", "Two Pointers", "Greedy"], "difficulty": "medium", "time_limit": 15,
            "boilerplate": {"python": "import json\nheight = json.loads(input())\ndef max_area(height):\n    pass\nprint(max_area(height))", "javascript": "const h = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction maxArea(h) { }\nconsole.log(maxArea(h));"}
        },
    ],
    "hard": [
        {
            "id": "bh1", "title": "Trapping Rain Water",
            "description": "Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
            "examples": [
                {"input": "height = [0,1,0,2,1,0,1,3,2,1,2,1]", "output": "6", "explanation": "6 units of water are trapped."},
                {"input": "height = [4,2,0,3,2,5]", "output": "9", "explanation": ""},
            ],
            "constraints": ["n == height.length", "1 ≤ n ≤ 2*10⁴"],
            "test_cases": [{"input": "[0,1,0,2,1,0,1,3,2,1,2,1]", "expected": "6"}, {"input": "[4,2,0,3,2,5]", "expected": "9"}],
            "tags": ["Array", "Two Pointers", "Dynamic Programming", "Stack"], "difficulty": "hard", "time_limit": 20,
            "boilerplate": {"python": "import json\nheight = json.loads(input())\ndef trap(height):\n    pass\nprint(trap(height))", "javascript": "const h = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8').trim());\nfunction trap(h) { }\nconsole.log(trap(h));"}
        },
        {
            "id": "bh2", "title": "Median of Two Sorted Arrays",
            "description": "Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays. The overall run time complexity should be O(log(m+n)).",
            "examples": [
                {"input": "nums1 = [1,3], nums2 = [2]", "output": "2.00000", "explanation": "Merged array = [1,2,3], median = 2."},
                {"input": "nums1 = [1,2], nums2 = [3,4]", "output": "2.50000", "explanation": "Merged array = [1,2,3,4], median = 2.5."},
            ],
            "constraints": ["0 ≤ m, n ≤ 1000"],
            "test_cases": [{"input": "[1,3]\n[2]", "expected": "2.0"}, {"input": "[1,2]\n[3,4]", "expected": "2.5"}],
            "tags": ["Array", "Binary Search", "Divide and Conquer"], "difficulty": "hard", "time_limit": 20,
            "boilerplate": {"python": "import json\nnums1 = json.loads(input())\nnums2 = json.loads(input())\ndef find_median(nums1, nums2):\n    pass\nprint(find_median(nums1, nums2))", "javascript": "const lines = require('fs').readFileSync('/dev/stdin','utf8').trim().split('\\n');\nconst nums1 = JSON.parse(lines[0]);\nconst nums2 = JSON.parse(lines[1]);\nfunction findMedian(n1, n2) { }\nconsole.log(findMedian(nums1, nums2));"}
        },
        {
            "id": "bh3", "title": "Longest Valid Parentheses",
            "description": "Given a string containing just the characters '(' and ')', return the length of the longest valid (well-formed) parentheses substring.",
            "examples": [
                {"input": "s = \"(()\"", "output": "2", "explanation": "Longest valid is '()'"},
                {"input": "s = \")()())\"", "output": "4", "explanation": "Longest valid is '()()'"},
            ],
            "constraints": ["0 ≤ s.length ≤ 3*10⁴"],
            "test_cases": [{"input": "(()", "expected": "2"}, {"input": ")()())", "expected": "4"}, {"input": "", "expected": "0"}],
            "tags": ["String", "Dynamic Programming", "Stack"], "difficulty": "hard", "time_limit": 20,
            "boilerplate": {"python": "s = input()\ndef longest_valid_parentheses(s):\n    pass\nprint(longest_valid_parentheses(s))", "javascript": "const s = require('fs').readFileSync('/dev/stdin','utf8').trim();\nfunction longestValidParentheses(s) { }\nconsole.log(longestValidParentheses(s));"}
        },
    ]
}

def _gen_duel_code():
    import random, string
    for _ in range(20):
        code = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=6))
        if code not in _duels:
            return code
    return "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))


def get_league(trophies: int) -> dict:
    """Get current league info from trophy count."""
    current = LEAGUES[0]
    current_idx = 0
    for i, league in enumerate(LEAGUES):
        if trophies >= league[0]:
            current = league
            current_idx = i
    # Next league
    next_league = None
    if current_idx + 1 < len(LEAGUES):
        nl = LEAGUES[current_idx + 1]
        next_league = {
            "name": f"{nl[1]} {nl[2]}".strip() if nl[2] else nl[1],
            "full_name": f"{nl[1]} {nl[2]}".strip(),
            "trophies_needed": nl[0] - trophies,
            "threshold": nl[0],
            "icon": nl[3],
        }
    # Progress within current league
    current_min = current[0]
    next_min    = LEAGUES[current_idx + 1][0] if current_idx + 1 < len(LEAGUES) else current[0] + 1000
    progress_pct = min(100, int(((trophies - current_min) / max(1, next_min - current_min)) * 100))

    full_name = f"{current[1]} {current[2]}".strip()
    return {
        "name": current[1],
        "tier": current[2],
        "full_name": full_name,
        "icon": current[3],
        "color": current[4],
        "badge_color": current[5],
        "trophies": trophies,
        "next": next_league,
        "progress_pct": progress_pct,
        "current_min": current_min,
        "next_min": next_min,
    }


def get_xp_rank(total_xp: int) -> dict:
    """Get XP rank from total XP earned."""
    current = XP_RANKS[0]
    current_idx = 0
    for i, rank in enumerate(XP_RANKS):
        if total_xp >= rank[0]:
            current = rank
            current_idx = i
    next_rank = None
    if current_idx + 1 < len(XP_RANKS):
        nr = XP_RANKS[current_idx + 1]
        next_rank = {"name": nr[1], "xp_needed": nr[0] - total_xp, "threshold": nr[0]}
    current_min = current[0]
    next_min    = XP_RANKS[current_idx+1][0] if current_idx+1 < len(XP_RANKS) else current[0]+1000
    progress_pct= min(100, int(((total_xp-current_min)/max(1,next_min-current_min))*100))
    return {
        "name": current[1],
        "icon": current[2],
        "color": current[3],
        "xp": total_xp,
        "next": next_rank,
        "progress_pct": progress_pct,
    }


def get_trophy_rewards(diff: str, result: str) -> tuple:
    """Returns (xp_change, trophy_change) for a battle result."""
    if result == "win":
        xp = {"easy":XP_WIN_EASY,"medium":XP_WIN_MEDIUM,"hard":XP_WIN_HARD}.get(diff,50)
        tr = {"easy":TROPHY_WIN_EASY,"medium":TROPHY_WIN_MEDIUM,"hard":TROPHY_WIN_HARD}.get(diff,15)
    elif result == "draw":
        xp, tr = XP_DRAW, TROPHY_DRAW
    else:
        xp = {"easy":XP_LOSE_EASY,"medium":XP_LOSE_MEDIUM,"hard":XP_LOSE_HARD}.get(diff,10)
        tr = {"easy":TROPHY_LOSE_EASY,"medium":TROPHY_LOSE_MEDIUM,"hard":TROPHY_LOSE_HARD}.get(diff,-3)
    return xp, tr


def get_battle_problem(difficulty: str, exclude_ids: list = None) -> dict:
    """Return a random problem for the given difficulty, excluding already-used ones."""
    pool = BATTLE_PROBLEMS.get(difficulty, BATTLE_PROBLEMS["easy"])
    exclude_ids = exclude_ids or []
    available = [p for p in pool if p["id"] not in exclude_ids]
    if not available:
        available = pool  # reset if all used
    return dict(random.choice(available))


def create_duel(host_id: int, host_name: str, host_image: str, difficulty: str, language: str) -> dict:
    code = _gen_duel_code()
    problem = get_battle_problem(difficulty)
    duel = {
        "duel_code": code,
        "host_id": host_id,
        "difficulty": difficulty,
        "language": language,
        "problem": problem,
        "status": "waiting",   # waiting → countdown → active → finished
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "finished_at": None,
        "time_limit": problem.get("time_limit", 15) * 60,  # seconds
        "players": {
            str(host_id): {
                "user_id": host_id,
                "name": host_name,
                "image": host_image,
                "sid": None,
                "code": problem.get("boilerplate", {}).get(language, "# Write your solution here\n"),
                "submitted": False,
                "passed": False,
                "passed_count": 0,
                "total_tests": len(problem.get("test_cases", [])),
                "submit_time": None,
                "xp_earned": 0,
                "ready": False,
                "result": None,
            }
        },
        "winner_id": None,
        "chat": [],
        "events": [],  # live event log: "Tushar passed test 1!", "Rahul submitted!"
    }
    _duels[code] = duel
    return duel


def get_duel(code: str) -> dict:
    return _duels.get((code or "").upper().strip())


def join_duel(code: str, user_id: int, user_name: str, user_image: str) -> dict:
    duel = get_duel(code)
    if not duel or duel["status"] not in ("waiting",):
        return None
    if len(duel["players"]) >= 2:
        return None  # full
    uid = str(user_id)
    if uid not in duel["players"]:
        problem = duel["problem"]
        lang = duel["language"]
        duel["players"][uid] = {
            "user_id": user_id,
            "name": user_name,
            "image": user_image,
            "sid": None,
            "code": problem.get("boilerplate", {}).get(lang, "# Write your solution here\n"),
            "submitted": False,
            "passed": False,
            "passed_count": 0,
            "total_tests": len(problem.get("test_cases", [])),
            "submit_time": None,
            "xp_earned": 0,
            "ready": False,
            "result": None,
        }
    return duel


def set_player_sid(code: str, user_id: int, sid: str):
    duel = get_duel(code)
    if duel and str(user_id) in duel["players"]:
        duel["players"][str(user_id)]["sid"] = sid


def set_player_ready(code: str, user_id: int) -> bool:
    duel = get_duel(code)
    if not duel: return False
    if str(user_id) in duel["players"]:
        duel["players"][str(user_id)]["ready"] = True
    # Check if both ready
    all_ready = all(p["ready"] for p in duel["players"].values())
    return all_ready and len(duel["players"]) == 2


def start_duel(code: str):
    duel = get_duel(code)
    if duel:
        duel["status"] = "active"
        duel["started_at"] = datetime.utcnow().isoformat()


def update_player_code(code: str, user_id: int, player_code: str):
    duel = get_duel(code)
    if duel and str(user_id) in duel["players"]:
        duel["players"][str(user_id)]["code"] = player_code


def record_test_pass(code: str, user_id: int, test_num: int) -> dict:
    duel = get_duel(code)
    if not duel: return {}
    p = duel["players"].get(str(user_id))
    if not p: return {}
    p["passed_count"] = max(p.get("passed_count", 0), test_num)
    event = f"⚡ {p['name']} passed test case {test_num}!"
    duel["events"].append({"text": event, "uid": user_id, "t": time.time()})
    return {"event": event, "player": p}


def submit_solution(code: str, user_id: int, passed: bool, passed_count: int, total: int, exec_time: float) -> dict:
    duel = get_duel(code)
    if not duel: return {}
    p = duel["players"].get(str(user_id))
    if not p or p.get("submitted"): return {}

    now = datetime.utcnow()
    p["submitted"] = True
    p["passed"] = passed
    p["passed_count"] = passed_count
    p["total_tests"] = total
    p["submit_time"] = now.isoformat()
    p["exec_time"] = exec_time

    result_text = "✅ ACCEPTED" if passed else f"❌ {passed_count}/{total} tests passed"
    p["result"] = result_text

    event = f"🏁 {p['name']} submitted — {result_text}"
    duel["events"].append({"text": event, "uid": user_id, "t": time.time()})

    # Check if duel should end
    all_submitted = all(pl["submitted"] for pl in duel["players"].values())
    any_passed    = any(pl["passed"] for pl in duel["players"].values())

    if all_submitted or (passed and any_passed):
        return _finish_duel(code, user_id if passed else None)

    return {"event": event, "finished": False, "player": p}


def _finish_duel(code: str, first_solver_id=None) -> dict:
    duel = get_duel(code)
    if not duel or duel["status"] == "finished": return {}

    duel["status"] = "finished"
    duel["finished_at"] = datetime.utcnow().isoformat()

    players = list(duel["players"].values())
    diff = duel["difficulty"]

    # Determine winner
    passed_players  = [p for p in players if p["passed"]]
    winner = None

    if len(passed_players) == 1:
        winner = passed_players[0]
    elif len(passed_players) == 2:
        # Both solved — whoever submitted first wins
        times = [(p, p.get("submit_time", "9999")) for p in passed_players]
        times.sort(key=lambda x: x[1])
        winner = times[0][0]
    elif len(passed_players) == 0:
        # Most test cases passed wins
        players.sort(key=lambda p: p.get("passed_count", 0), reverse=True)
        if players[0].get("passed_count", 0) > players[1].get("passed_count", 0):
            winner = players[0]

    # Calculate XP
    xp_win  = {"easy": XP_WIN_EASY,  "medium": XP_WIN_MEDIUM,  "hard": XP_WIN_HARD }.get(diff, 50)
    xp_lose = {"easy": XP_LOSE_EASY, "medium": XP_LOSE_MEDIUM, "hard": XP_LOSE_HARD}.get(diff, 10)

    for p in players:
        if winner and p["user_id"] == winner["user_id"]:
            p["xp_earned"] = xp_win
        elif winner is None:
            p["xp_earned"] = XP_DRAW
        else:
            p["xp_earned"] = xp_lose

    duel["winner_id"] = winner["user_id"] if winner else None

    winner_name = winner["name"] if winner else "Draw"
    duel["events"].append({"text": f"🏆 Duel over! Winner: {winner_name}", "uid": 0, "t": time.time()})

    # Update XP/trophies in each player record inside the duel
    for p in duel["players"].values():
        if winner and p["user_id"] == winner["user_id"]:
            xp, tr = get_trophy_rewards(diff, "win")
        elif winner is None:
            xp, tr = get_trophy_rewards(diff, "draw")
        else:
            xp, tr = get_trophy_rewards(diff, "loss")
        p["xp_earned"]      = xp
        p["trophy_change"]   = tr

    # Save to DB (non-blocking attempt)
    try:
        save_battle_result(duel)
    except Exception as e:
        print(f"[Battle] save_battle_result failed: {e}")

    return {"finished": True, "winner_id": duel["winner_id"], "players": list(duel["players"].values()), "duel": duel}



def next_question_for_all(code: str, requested_by_id: int) -> dict:
    """Load a new question and reset ALL players — available to BOTH players after a round ends."""
    duel = get_duel(code)
    if not duel:
        return {"error": "Duel not found"}
    exclude = [duel["problem"]["id"]]
    new_problem = get_battle_problem(duel["difficulty"], exclude_ids=exclude)
    duel["problem"] = new_problem
    duel["time_limit"] = new_problem.get("time_limit", 15) * 60
    duel["winner_id"] = None
    duel["status"] = "active"
    duel["started_at"] = datetime.utcnow().isoformat()
    for p in duel["players"].values():
        p["submitted"] = False
        p["passed"] = False
        p["passed_count"] = 0
        p["total_tests"] = len(new_problem.get("test_cases", []))
        p["submit_time"] = None
        p["xp_earned"] = 0
        p["result"] = None
        p["code"] = new_problem.get("boilerplate", {}).get(duel["language"], "# Write your solution here\n")
    requester_name = duel["players"].get(str(requested_by_id), {}).get("name", "A player")
    duel["events"].append({"text": f"\U0001f504 {requester_name} loaded a new question! Battle continues!", "uid": requested_by_id, "t": time.time()})
    return {"success": True, "state": duel_state(code)}


def add_chat(code: str, user_id: int, user_name: str, message: str) -> dict:
    duel = get_duel(code)
    entry = {"user_id": user_id, "name": user_name, "message": message,
             "time": datetime.utcnow().strftime("%H:%M")}
    if duel:
        duel["chat"].append(entry)
    return entry


def duel_state(code: str) -> dict:
    duel = get_duel(code)
    if not duel: return None
    return {
        "duel_code": duel["duel_code"],
        "host_id": duel["host_id"],
        "difficulty": duel["difficulty"],
        "language": duel["language"],
        "status": duel["status"],
        "problem": duel["problem"],
        "players": list(duel["players"].values()),
        "winner_id": duel["winner_id"],
        "chat": duel["chat"][-30:],
        "events": duel["events"][-20:],
        "started_at": duel["started_at"],
        "time_limit": duel["time_limit"],
    }


# ═══════════════════════════════════════════════════════════════
#  DATABASE PERSISTENCE
# ═══════════════════════════════════════════════════════════════

def save_battle_result(duel: dict):
    """Save battle result to DB — updates BattleProfile + creates BattleHistory rows."""
    try:
        from flask import current_app
        from backend.extensions import db
        from backend.models import BattleProfile, BattleHistory
        import json

        players = list(duel["players"].values())
        diff    = duel["difficulty"]
        winner_id = duel.get("winner_id")

        for p in players:
            uid = p["user_id"]
            if not uid: continue

            # Determine result
            if winner_id is None:
                result = "draw"
            elif p["user_id"] == winner_id:
                result = "win"
            else:
                result = "loss"

            xp_change, trophy_change = get_trophy_rewards(diff, result)

            # Upsert BattleProfile
            bp = BattleProfile.query.filter_by(user_id=uid).first()
            if not bp:
                bp = BattleProfile(user_id=uid)
                db.session.add(bp)

            bp.total_xp    += xp_change
            bp.battle_xp   += xp_change
            bp.total_battles += 1
            bp.total_tests_passed   += p.get("passed_count", 0)
            bp.total_tests_attempted += p.get("total_tests", 0)

            # Trophies (never go below 0)
            bp.trophies = max(0, bp.trophies + trophy_change)

            if result == "win":
                bp.wins += 1
                bp.current_streak += 1
                bp.best_streak = max(bp.best_streak, bp.current_streak)
                if diff == "easy":   bp.easy_wins   += 1
                elif diff == "medium": bp.medium_wins += 1
                elif diff == "hard":   bp.hard_wins   += 1
            elif result == "loss":
                bp.losses += 1
                bp.current_streak = 0
            else:
                bp.draws += 1

            # Find opponent
            opp = next((pl for pl in players if pl["user_id"] != uid), None)
            opp_id   = opp["user_id"] if opp else None
            opp_name = opp["name"] if opp else "Unknown"

            # BattleHistory row
            hist = BattleHistory(
                user_id        = uid,
                opponent_id    = opp_id,
                opponent_name  = opp_name,
                duel_code      = duel["duel_code"],
                difficulty     = diff,
                language       = duel["language"],
                problem_id     = duel["problem"].get("id"),
                problem_title  = duel["problem"].get("title"),
                result         = result,
                xp_earned      = xp_change,
                trophies_change= trophy_change,
                tests_passed   = p.get("passed_count", 0),
                total_tests    = p.get("total_tests", 0),
                submitted      = p.get("submitted", False),
                accepted       = p.get("passed", False),
            )
            db.session.add(hist)

        db.session.commit()
        print(f"[Battle] Saved result for duel {duel["duel_code"]}" )
    except Exception as e:
        print(f"[Battle] DB save error: {e}")
        try:
            from backend.extensions import db
            db.session.rollback()
        except: pass


def get_battle_profile(user_id: int) -> dict:
    """Get user battle profile with league + XP rank info."""
    try:
        from backend.models import BattleProfile, BattleHistory
        bp = BattleProfile.query.filter_by(user_id=user_id).first()
        if not bp:
            return {
                "total_xp": 0, "trophies": 0, "total_battles": 0,
                "wins": 0, "losses": 0, "draws": 0,
                "current_streak": 0, "best_streak": 0,
                "easy_wins": 0, "medium_wins": 0, "hard_wins": 0,
                "total_tests_passed": 0, "total_tests_attempted": 0,
                "win_rate": 0,
                "league": get_league(0),
                "xp_rank": get_xp_rank(0),
            }
        win_rate = round((bp.wins / max(1, bp.total_battles)) * 100, 1)
        return {
            "total_xp": bp.total_xp,
            "battle_xp": bp.battle_xp,
            "trophies": bp.trophies,
            "total_battles": bp.total_battles,
            "wins": bp.wins,
            "losses": bp.losses,
            "draws": bp.draws,
            "current_streak": bp.current_streak,
            "best_streak": bp.best_streak,
            "easy_wins": bp.easy_wins,
            "medium_wins": bp.medium_wins,
            "hard_wins": bp.hard_wins,
            "total_tests_passed": bp.total_tests_passed,
            "total_tests_attempted": bp.total_tests_attempted,
            "win_rate": win_rate,
            "league": get_league(bp.trophies),
            "xp_rank": get_xp_rank(bp.total_xp),
        }
    except Exception as e:
        print(f"[Battle] get_battle_profile error: {e}")
        return {"total_xp": 0, "trophies": 0, "total_battles": 0, "wins": 0,
                "losses": 0, "draws": 0, "win_rate": 0,
                "league": get_league(0), "xp_rank": get_xp_rank(0)}


def get_battle_history(user_id: int, limit: int = 20) -> list:
    """Get recent battle history for a user."""
    try:
        from backend.models import BattleHistory
        rows = BattleHistory.query.filter_by(user_id=user_id).order_by(
            BattleHistory.played_at.desc()
        ).limit(limit).all()
        result = []
        for r in rows:
            result.append({
                "id": r.id,
                "duel_code": r.duel_code,
                "opponent_name": r.opponent_name,
                "difficulty": r.difficulty,
                "language": r.language,
                "problem_title": r.problem_title,
                "result": r.result,
                "xp_earned": r.xp_earned,
                "trophies_change": r.trophies_change,
                "tests_passed": r.tests_passed,
                "total_tests": r.total_tests,
                "accepted": r.accepted,
                "played_at": r.played_at.strftime("%b %d, %Y %H:%M") if r.played_at else "",
            })
        return result
    except Exception as e:
        print(f"[Battle] get_battle_history error: {e}")
        return []