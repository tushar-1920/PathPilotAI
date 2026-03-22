"""
PathPilot AI — Problem Service
Contains ALL problem IDs so the backend never 404s on run-code or submit-code.
IDs must exactly match the frontend JS PROBLEMS array ids.
"""

from typing import List, Dict, Optional, Any

# ─────────────────────────────────────────────────────────────────────────────
#  COMPLETE PROBLEM DATABASE  (195 problems matching frontend)
# ─────────────────────────────────────────────────────────────────────────────

PROBLEMS_DB: List[Dict[str, Any]] = [

# ── EASY ──────────────────────────────────────────────────────────────────────
{"id":1,"title":"Two Sum","difficulty":"Easy","topics":["Array","Hash Table"],"acceptance":49.1,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[2,7,11,15]\n9","expected_output":"[0, 1]","hidden":False},
   {"input":"[3,2,4]\n6","expected_output":"[1, 2]","hidden":False},
   {"input":"[3,3]\n6","expected_output":"[0, 1]","hidden":True},
 ]},

{"id":2,"title":"Valid Parentheses","difficulty":"Easy","topics":["String","Stack"],"acceptance":40.5,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":'"()"',"expected_output":"true","hidden":False},
   {"input":'"()[]{}"',"expected_output":"true","hidden":False},
   {"input":'"(]"',"expected_output":"false","hidden":False},
   {"input":'"([)]"',"expected_output":"false","hidden":True},
 ]},

{"id":3,"title":"Climbing Stairs","difficulty":"Easy","topics":["Dynamic Programming","Math"],"acceptance":51.9,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"2","expected_output":"2","hidden":False},
   {"input":"3","expected_output":"3","hidden":False},
   {"input":"10","expected_output":"89","hidden":True},
 ]},

{"id":4,"title":"Best Time to Buy and Sell Stock","difficulty":"Easy","topics":["Array","Dynamic Programming"],"acceptance":54.2,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[7,1,5,3,6,4]","expected_output":"5","hidden":False},
   {"input":"[7,6,4,3,1]","expected_output":"0","hidden":False},
   {"input":"[1,2]","expected_output":"1","hidden":True},
 ]},

{"id":5,"title":"Contains Duplicate","difficulty":"Easy","topics":["Array","Hash Table","Sorting"],"acceptance":60.1,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,2,3,1]","expected_output":"true","hidden":False},
   {"input":"[1,2,3,4]","expected_output":"false","hidden":False},
   {"input":"[1,1,1,3,3,4,3,2,4,2]","expected_output":"true","hidden":True},
 ]},

{"id":6,"title":"Valid Anagram","difficulty":"Easy","topics":["Hash Table","String","Sorting"],"acceptance":62.9,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":'"anagram"\n"nagaram"',"expected_output":"true","hidden":False},
   {"input":'"rat"\n"car"',"expected_output":"false","hidden":False},
 ]},

{"id":7,"title":"Reverse Linked List","difficulty":"Easy","topics":["Linked List","Recursion"],"acceptance":73.6,
 "plans":["Blind 75","NeetCode 150","Top Interview 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,2,3,4,5]","expected_output":"[5, 4, 3, 2, 1]","hidden":False},
   {"input":"[1,2]","expected_output":"[2, 1]","hidden":False},
   {"input":"[]","expected_output":"[]","hidden":True},
 ]},

{"id":8,"title":"Merge Two Sorted Lists","difficulty":"Easy","topics":["Linked List","Recursion"],"acceptance":61.3,
 "plans":["Blind 75","NeetCode 150","Top Interview 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,2,4]\n[1,3,4]","expected_output":"[1, 1, 2, 3, 4, 4]","hidden":False},
   {"input":"[]\n[]","expected_output":"[]","hidden":False},
 ]},

{"id":9,"title":"Linked List Cycle","difficulty":"Easy","topics":["Linked List","Two Pointers"],"acceptance":45.8,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[{"input":"true_cycle","expected_output":"true","hidden":False}]},

{"id":10,"title":"Maximum Depth of Binary Tree","difficulty":"Easy","topics":["Tree","DFS","BFS"],"acceptance":73.2,
 "plans":["Blind 75","NeetCode 150","Top Interview 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[3,9,20,null,null,15,7]","expected_output":"3","hidden":False},
   {"input":"[1,null,2]","expected_output":"2","hidden":False},
 ]},

{"id":11,"title":"Same Tree","difficulty":"Easy","topics":["Tree","DFS"],"acceptance":56.2,
 "plans":["NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[{"input":"equal","expected_output":"true","hidden":False}]},

{"id":12,"title":"Invert Binary Tree","difficulty":"Easy","topics":["Tree","DFS"],"acceptance":75.3,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[{"input":"[4,2,7,1,3,6,9]","expected_output":"[4,7,2,9,6,3,1]","hidden":False}]},

{"id":13,"title":"Symmetric Tree","difficulty":"Easy","topics":["Tree","DFS"],"acceptance":52.4,
 "plans":["Top Interview 150"],"time_limit_ms":2000,
 "test_cases":[{"input":"symmetric","expected_output":"true","hidden":False}]},

{"id":14,"title":"Convert Sorted Array to BST","difficulty":"Easy","topics":["Array","Divide and Conquer","Tree"],"acceptance":68.4,
 "plans":[],"time_limit_ms":2000,"test_cases":[{"input":"[-10,-3,0,5,9]","expected_output":"balanced BST","hidden":False}]},

{"id":15,"title":"Balanced Binary Tree","difficulty":"Easy","topics":["Tree","DFS"],"acceptance":48.2,
 "plans":["NeetCode 150"],"time_limit_ms":2000,"test_cases":[{"input":"balanced","expected_output":"true","hidden":False}]},

{"id":16,"title":"Single Number","difficulty":"Easy","topics":["Array","Bit Manipulation"],"acceptance":70.2,
 "plans":["NeetCode 150","Top Interview 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[2,2,1]","expected_output":"1","hidden":False},
   {"input":"[4,1,2,1,2]","expected_output":"4","hidden":False},
   {"input":"[1]","expected_output":"1","hidden":True},
 ]},

{"id":17,"title":"Missing Number","difficulty":"Easy","topics":["Array","Math","Bit Manipulation"],"acceptance":61.4,
 "plans":["NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[3,0,1]","expected_output":"2","hidden":False},
   {"input":"[0,1]","expected_output":"2","hidden":False},
 ]},

{"id":18,"title":"Counting Bits","difficulty":"Easy","topics":["Dynamic Programming","Bit Manipulation"],"acceptance":74.8,
 "plans":["NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"2","expected_output":"[0, 1, 1]","hidden":False},
   {"input":"5","expected_output":"[0, 1, 1, 2, 1, 2]","hidden":False},
 ]},

{"id":19,"title":"Number of 1 Bits","difficulty":"Easy","topics":["Bit Manipulation"],"acceptance":67.2,
 "plans":["NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[{"input":"11","expected_output":"3","hidden":False}]},

{"id":20,"title":"Reverse Bits","difficulty":"Easy","topics":["Bit Manipulation"],"acceptance":51.4,
 "plans":["NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[{"input":"43261596","expected_output":"964176192","hidden":False}]},

# ── MEDIUM ─────────────────────────────────────────────────────────────────────
{"id":21,"title":"Maximum Subarray","difficulty":"Medium","topics":["Array","Dynamic Programming"],"acceptance":49.6,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[-2,1,-3,4,-1,2,1,-5,4]","expected_output":"6","hidden":False},
   {"input":"[1]","expected_output":"1","hidden":False},
   {"input":"[-2,-1]","expected_output":"-1","hidden":True},
 ]},

{"id":22,"title":"Longest Substring Without Repeating Characters","difficulty":"Medium","topics":["Hash Table","String","Sliding Window"],"acceptance":33.8,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":'"abcabcbb"',"expected_output":"3","hidden":False},
   {"input":'"bbbbb"',"expected_output":"1","hidden":False},
   {"input":'"pwwkew"',"expected_output":"3","hidden":False},
   {"input":'""',"expected_output":"0","hidden":True},
 ]},

{"id":23,"title":"3Sum","difficulty":"Medium","topics":["Array","Two Pointers","Sorting"],"acceptance":29.7,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[-1,0,1,2,-1,-4]","expected_output":"[[-1, -1, 2], [-1, 0, 1]]","hidden":False},
   {"input":"[0,0,0]","expected_output":"[[0, 0, 0]]","hidden":False},
 ]},

{"id":24,"title":"Container With Most Water","difficulty":"Medium","topics":["Array","Two Pointers","Greedy"],"acceptance":54.2,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,8,6,2,5,4,8,3,7]","expected_output":"49","hidden":False},
   {"input":"[1,1]","expected_output":"1","hidden":False},
 ]},

{"id":25,"title":"Merge Intervals","difficulty":"Medium","topics":["Array","Sorting"],"acceptance":45.8,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[[1,3],[2,6],[8,10],[15,18]]","expected_output":"[[1, 6], [8, 10], [15, 18]]","hidden":False},
   {"input":"[[1,4],[4,5]]","expected_output":"[[1, 5]]","hidden":False},
 ]},

{"id":26,"title":"Group Anagrams","difficulty":"Medium","topics":["Array","Hash Table","String","Sorting"],"acceptance":64.8,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":'["eat","tea","tan","ate","nat","bat"]',
    "expected_output":'[["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]',"hidden":False},
 ]},

{"id":27,"title":"Product of Array Except Self","difficulty":"Medium","topics":["Array","Prefix Sum"],"acceptance":64.4,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,2,3,4]","expected_output":"[24, 12, 8, 6]","hidden":False},
   {"input":"[-1,1,0,-3,3]","expected_output":"[0, 0, 9, 0, 0]","hidden":False},
 ]},

{"id":28,"title":"Find Minimum in Rotated Sorted Array","difficulty":"Medium","topics":["Array","Binary Search"],"acceptance":47.8,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[3,4,5,1,2]","expected_output":"1","hidden":False},
   {"input":"[4,5,6,7,0,1,2]","expected_output":"0","hidden":False},
 ]},

{"id":29,"title":"Search in Rotated Sorted Array","difficulty":"Medium","topics":["Array","Binary Search"],"acceptance":38.9,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[4,5,6,7,0,1,2]\n0","expected_output":"4","hidden":False},
   {"input":"[4,5,6,7,0,1,2]\n3","expected_output":"-1","hidden":False},
 ]},

{"id":30,"title":"Coin Change","difficulty":"Medium","topics":["Array","Dynamic Programming","BFS"],"acceptance":42.1,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,2,5]\n11","expected_output":"3","hidden":False},
   {"input":"[2]\n3","expected_output":"-1","hidden":False},
   {"input":"[1,5,11]\n11","expected_output":"1","hidden":True},
 ]},

{"id":31,"title":"Longest Increasing Subsequence","difficulty":"Medium","topics":["Array","Binary Search","Dynamic Programming"],"acceptance":54.1,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[10,9,2,5,3,7,101,18]","expected_output":"4","hidden":False},
   {"input":"[0,1,0,3,2,3]","expected_output":"4","hidden":False},
   {"input":"[7,7,7,7]","expected_output":"1","hidden":True},
 ]},

{"id":32,"title":"House Robber","difficulty":"Medium","topics":["Array","Dynamic Programming"],"acceptance":49.5,
 "plans":["Blind 75","NeetCode 150","Top Interview 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,2,3,1]","expected_output":"4","hidden":False},
   {"input":"[2,7,9,3,1]","expected_output":"12","hidden":False},
 ]},

{"id":33,"title":"House Robber II","difficulty":"Medium","topics":["Array","Dynamic Programming"],"acceptance":39.8,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[2,3,2]","expected_output":"3","hidden":False},
   {"input":"[1,2,3,1]","expected_output":"4","hidden":False},
 ]},

{"id":34,"title":"Decode Ways","difficulty":"Medium","topics":["String","Dynamic Programming"],"acceptance":30.8,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":'"12"',"expected_output":"2","hidden":False},
   {"input":'"226"',"expected_output":"3","hidden":False},
   {"input":'"06"',"expected_output":"0","hidden":True},
 ]},

{"id":35,"title":"Unique Paths","difficulty":"Medium","topics":["Math","Dynamic Programming"],"acceptance":62.9,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"3\n7","expected_output":"28","hidden":False},
   {"input":"3\n2","expected_output":"3","hidden":False},
 ]},

{"id":36,"title":"Jump Game","difficulty":"Medium","topics":["Array","Dynamic Programming","Greedy"],"acceptance":38.4,
 "plans":["Blind 75","NeetCode 150","Top Interview 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[2,3,1,1,4]","expected_output":"true","hidden":False},
   {"input":"[3,2,1,0,4]","expected_output":"false","hidden":False},
 ]},

{"id":37,"title":"Word Search","difficulty":"Medium","topics":["Array","Backtracking","Matrix"],"acceptance":40.8,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":3000,
 "test_cases":[{"input":"grid,ABCCED","expected_output":"true","hidden":False}]},

{"id":38,"title":"Number of Islands","difficulty":"Medium","topics":["Array","DFS","BFS","Matrix"],"acceptance":55.3,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":'[["1","1","0"],["0","1","0"],["0","0","1"]]',"expected_output":"2","hidden":False},
 ]},

{"id":39,"title":"Course Schedule","difficulty":"Medium","topics":["DFS","BFS","Graph","Topological Sort"],"acceptance":45.7,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"2\n[[1,0]]","expected_output":"true","hidden":False},
   {"input":"2\n[[1,0],[0,1]]","expected_output":"false","hidden":False},
 ]},

{"id":40,"title":"LRU Cache","difficulty":"Medium","topics":["Hash Table","Linked List","Design"],"acceptance":40.3,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":3000,
 "test_cases":[{"input":"2\noperations","expected_output":"see problem","hidden":False}]},

{"id":41,"title":"Validate Binary Search Tree","difficulty":"Medium","topics":["Tree","DFS","BST"],"acceptance":32.0,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[2,1,3]","expected_output":"true","hidden":False},
   {"input":"[5,1,4,null,null,3,6]","expected_output":"false","hidden":False},
 ]},

{"id":42,"title":"Binary Tree Level Order Traversal","difficulty":"Medium","topics":["Tree","BFS"],"acceptance":64.3,
 "plans":["Blind 75","NeetCode 150","Top Interview 150"],"time_limit_ms":2000,
 "test_cases":[{"input":"[3,9,20,null,null,15,7]","expected_output":"[[3], [9, 20], [15, 7]]","hidden":False}]},

{"id":43,"title":"Rotting Oranges","difficulty":"Medium","topics":["Array","BFS","Matrix"],"acceptance":52.2,
 "plans":["NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[[2,1,1],[1,1,0],[0,1,1]]","expected_output":"4","hidden":False},
   {"input":"[[2,1,1],[0,1,1],[1,0,1]]","expected_output":"-1","hidden":False},
 ]},

{"id":44,"title":"Pacific Atlantic Water Flow","difficulty":"Medium","topics":["Array","DFS","BFS","Matrix"],"acceptance":52.6,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":3000,
 "test_cases":[{"input":"heights","expected_output":"coordinates","hidden":False}]},

{"id":45,"title":"Min Stack","difficulty":"Medium","topics":["Stack","Design"],"acceptance":51.4,
 "plans":["NeetCode 150","Top Interview 150"],"time_limit_ms":2000,
 "test_cases":[{"input":"operations","expected_output":"[-3, 0, -2]","hidden":False}]},

{"id":46,"title":"Daily Temperatures","difficulty":"Medium","topics":["Array","Stack","Monotonic Stack"],"acceptance":66.4,
 "plans":["NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[73,74,75,71,69,72,76,73]","expected_output":"[1, 1, 4, 2, 1, 1, 0, 0]","hidden":False},
   {"input":"[30,40,50,60]","expected_output":"[1, 1, 1, 0]","hidden":False},
 ]},

{"id":47,"title":"Top K Frequent Elements","difficulty":"Medium","topics":["Array","Hash Table","Sorting","Heap"],"acceptance":63.2,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,1,1,2,2,3]\n2","expected_output":"[1, 2]","hidden":False},
   {"input":"[1]\n1","expected_output":"[1]","hidden":False},
 ]},

{"id":48,"title":"Kth Largest Element in an Array","difficulty":"Medium","topics":["Array","Divide and Conquer","Sorting","Heap"],"acceptance":64.5,
 "plans":["NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[3,2,1,5,6,4]\n2","expected_output":"5","hidden":False},
   {"input":"[3,2,3,1,2,4,5,5,6]\n4","expected_output":"4","hidden":False},
 ]},

{"id":49,"title":"Combination Sum","difficulty":"Medium","topics":["Array","Backtracking"],"acceptance":67.8,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[2,3,6,7]\n7","expected_output":"[[2, 2, 3], [7]]","hidden":False},
 ]},

{"id":50,"title":"Permutations","difficulty":"Medium","topics":["Array","Backtracking"],"acceptance":74.1,
 "plans":["Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,2,3]","expected_output":"6 permutations","hidden":False},
   {"input":"[0,1]","expected_output":"[[0, 1], [1, 0]]","hidden":False},
 ]},

{"id":51,"title":"Subsets","difficulty":"Medium","topics":["Array","Backtracking","Bit Manipulation"],"acceptance":74.9,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,2,3]","expected_output":"8 subsets","hidden":False},
   {"input":"[0]","expected_output":"[[], [0]]","hidden":False},
 ]},

{"id":52,"title":"Word Break","difficulty":"Medium","topics":["Hash Table","String","Dynamic Programming"],"acceptance":44.8,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":'"leetcode"\n["leet","code"]',"expected_output":"true","hidden":False},
   {"input":'"catsandog"\n["cats","dog","sand","and","cat"]',"expected_output":"false","hidden":False},
 ]},

{"id":53,"title":"Coin Change II","difficulty":"Medium","topics":["Array","Dynamic Programming"],"acceptance":58.7,
 "plans":["NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"5\n[1,2,5]","expected_output":"4","hidden":False},
   {"input":"3\n[2]","expected_output":"0","hidden":False},
 ]},

{"id":54,"title":"Longest Common Subsequence","difficulty":"Medium","topics":["String","Dynamic Programming"],"acceptance":56.3,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":'"abcde"\n"ace"',"expected_output":"3","hidden":False},
   {"input":'"abc"\n"abc"',"expected_output":"3","hidden":False},
   {"input":'"abc"\n"def"',"expected_output":"0","hidden":True},
 ]},

{"id":55,"title":"Partition Equal Subset Sum","difficulty":"Medium","topics":["Array","Dynamic Programming"],"acceptance":46.5,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,5,11,5]","expected_output":"true","hidden":False},
   {"input":"[1,2,3,5]","expected_output":"false","hidden":False},
 ]},

{"id":56,"title":"Clone Graph","difficulty":"Medium","topics":["Hash Table","DFS","BFS","Graph"],"acceptance":54.1,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[{"input":"graph","expected_output":"cloned graph","hidden":False}]},

{"id":57,"title":"Spiral Matrix","difficulty":"Medium","topics":["Array","Matrix","Simulation"],"acceptance":46.9,
 "plans":["Top Interview 150"],"time_limit_ms":2000,
 "test_cases":[{"input":"[[1,2,3],[4,5,6],[7,8,9]]","expected_output":"[1, 2, 3, 6, 9, 8, 7, 4, 5]","hidden":False}]},

{"id":58,"title":"Rotate Image","difficulty":"Medium","topics":["Array","Math","Matrix"],"acceptance":68.7,
 "plans":["Top Interview 150"],"time_limit_ms":2000,
 "test_cases":[{"input":"[[1,2,3],[4,5,6],[7,8,9]]","expected_output":"[[7,4,1],[8,5,2],[9,6,3]]","hidden":False}]},

{"id":59,"title":"Search a 2D Matrix","difficulty":"Medium","topics":["Array","Binary Search","Matrix"],"acceptance":44.3,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[[1,3,5,7],[10,11,16,20],[23,30,34,60]]\n3","expected_output":"true","hidden":False},
   {"input":"[[1,3,5,7],[10,11,16,20],[23,30,34,60]]\n13","expected_output":"false","hidden":False},
 ]},

{"id":60,"title":"Implement Trie","difficulty":"Medium","topics":["Hash Table","String","Design","Trie"],"acceptance":58.8,
 "plans":["Blind 75","NeetCode 150"],"time_limit_ms":2000,
 "test_cases":[{"input":"operations","expected_output":"[null,true,false,true,null,true]","hidden":False}]},

# ── HARD ──────────────────────────────────────────────────────────────────────
{"id":61,"title":"Trapping Rain Water","difficulty":"Hard","topics":["Array","Two Pointers","Dynamic Programming","Stack"],"acceptance":57.9,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[0,1,0,2,1,0,1,3,2,1,2,1]","expected_output":"6","hidden":False},
   {"input":"[4,2,0,3,2,5]","expected_output":"9","hidden":False},
   {"input":"[3,0,2,0,4]","expected_output":"7","hidden":True},
 ]},

{"id":62,"title":"Median of Two Sorted Arrays","difficulty":"Hard","topics":["Array","Binary Search","Divide and Conquer"],"acceptance":36.2,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,3]\n[2]","expected_output":"2.0","hidden":False},
   {"input":"[1,2]\n[3,4]","expected_output":"2.5","hidden":False},
 ]},

{"id":63,"title":"Merge K Sorted Lists","difficulty":"Hard","topics":["Linked List","Heap","Divide and Conquer"],"acceptance":48.3,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[[1,4,5],[1,3,4],[2,6]]","expected_output":"[1, 1, 2, 3, 4, 4, 5, 6]","hidden":False},
   {"input":"[]","expected_output":"[]","hidden":False},
 ]},

{"id":64,"title":"Binary Tree Maximum Path Sum","difficulty":"Hard","topics":["Tree","DFS","Dynamic Programming"],"acceptance":38.9,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,2,3]","expected_output":"6","hidden":False},
   {"input":"[-10,9,20,null,null,15,7]","expected_output":"42","hidden":False},
 ]},

{"id":65,"title":"Longest Consecutive Sequence","difficulty":"Hard","topics":["Array","Hash Table","Union Find"],"acceptance":44.8,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[100,4,200,1,3,2]","expected_output":"4","hidden":False},
   {"input":"[0,3,7,2,5,8,4,6,0,1]","expected_output":"9","hidden":False},
 ]},

{"id":66,"title":"Largest Rectangle in Histogram","difficulty":"Hard","topics":["Array","Stack","Monotonic Stack"],"acceptance":43.6,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[2,1,5,6,2,3]","expected_output":"10","hidden":False},
   {"input":"[2,4]","expected_output":"4","hidden":False},
 ]},

{"id":67,"title":"Sliding Window Maximum","difficulty":"Hard","topics":["Array","Queue","Sliding Window","Monotonic Queue"],"acceptance":46.8,
 "plans":["Blind 75","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,3,-1,-3,5,3,6,7]\n3","expected_output":"[3, 3, 5, 5, 6, 7]","hidden":False},
   {"input":"[1]\n1","expected_output":"[1]","hidden":False},
 ]},

{"id":68,"title":"Minimum Window Substring","difficulty":"Hard","topics":["Hash Table","String","Sliding Window"],"acceptance":40.7,
 "plans":["Blind 75","NeetCode 150","Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":'"ADOBECODEBANC"\n"ABC"',"expected_output":'"BANC"',"hidden":False},
   {"input":'"a"\n"a"',"expected_output":'"a"',"hidden":False},
 ]},

{"id":69,"title":"Word Ladder","difficulty":"Hard","topics":["Hash Table","String","BFS"],"acceptance":36.8,
 "plans":["FAANG Prep"],"time_limit_ms":3000,
 "test_cases":[{"input":'"hit"\n"cog"\n["hot","dot","dog","lot","log","cog"]',"expected_output":"5","hidden":False}]},

{"id":70,"title":"N-Queens","difficulty":"Hard","topics":["Array","Backtracking"],"acceptance":67.4,
 "plans":["FAANG Prep"],"time_limit_ms":3000,
 "test_cases":[
   {"input":"4","expected_output":"2 solutions","hidden":False},
   {"input":"1","expected_output":'[["Q"]]',"hidden":False},
 ]},

{"id":71,"title":"Serialize and Deserialize Binary Tree","difficulty":"Hard","topics":["String","Tree","DFS","BFS","Design"],"acceptance":56.3,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":3000,
 "test_cases":[{"input":"[1,2,3,null,null,4,5]","expected_output":"same tree","hidden":False}]},

{"id":72,"title":"Find Median from Data Stream","difficulty":"Hard","topics":["Two Pointers","Design","Sorting","Heap"],"acceptance":51.1,
 "plans":["Blind 75","NeetCode 150","FAANG Prep"],"time_limit_ms":3000,
 "test_cases":[{"input":"[1,2,3]","expected_output":"1.5 then 2.0","hidden":False}]},

{"id":73,"title":"Regular Expression Matching","difficulty":"Hard","topics":["String","Dynamic Programming","Recursion"],"acceptance":28.1,
 "plans":["FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":'"aa"\n"a"',"expected_output":"false","hidden":False},
   {"input":'"aa"\n"a*"',"expected_output":"true","hidden":False},
   {"input":'"ab"\n".*"',"expected_output":"true","hidden":False},
 ]},

{"id":74,"title":"Jump Game II","difficulty":"Medium","topics":["Array","Dynamic Programming","Greedy"],"acceptance":39.7,
 "plans":["NeetCode 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[2,3,1,1,4]","expected_output":"2","hidden":False},
   {"input":"[2,3,0,1,4]","expected_output":"2","hidden":False},
 ]},

{"id":75,"title":"Gas Station","difficulty":"Medium","topics":["Array","Greedy"],"acceptance":44.5,
 "plans":["Top Interview 150","FAANG Prep"],"time_limit_ms":2000,
 "test_cases":[
   {"input":"[1,2,3,4,5]\n[3,4,5,1,2]","expected_output":"3","hidden":False},
   {"input":"[2,3,4]\n[3,4,3]","expected_output":"-1","hidden":False},
 ]},
]

# ── Auto-generate stub entries for IDs 76–195 (EXTRA problems from frontend) ──
_EXTRA = [
 (76,"First Bad Version","Easy"),(77,"Sqrt(x)","Easy"),(78,"Power of Two","Easy"),
 (79,"Palindrome Number","Easy"),(80,"Roman to Integer","Easy"),
 (81,"Longest Common Prefix","Easy"),(82,"Remove Element","Easy"),
 (83,"Remove Duplicates from Sorted Array","Easy"),(84,"Merge Sorted Array","Easy"),
 (85,"Is Subsequence","Easy"),(86,"Move Zeroes","Easy"),(87,"Fibonacci Number","Easy"),
 (88,"Pascal's Triangle","Easy"),(89,"Find the Index of First Occurrence","Easy"),
 (90,"Ransom Note","Easy"),(91,"Word Pattern","Easy"),(92,"Isomorphic Strings","Easy"),
 (93,"Valid Palindrome","Easy"),(94,"Implement Queue using Stacks","Easy"),
 (95,"Power of Three","Easy"),(96,"Binary Search","Easy"),
 (97,"Guess Number Higher or Lower","Easy"),(98,"Search Insert Position","Easy"),
 (99,"Symmetric Tree","Easy"),(100,"Path Sum","Easy"),
 (101,"Diameter of Binary Tree","Easy"),(102,"Lowest Common Ancestor of BST","Easy"),
 (103,"Flood Fill","Easy"),(104,"K Closest Points to Origin","Medium"),
 (105,"Task Scheduler","Medium"),(106,"Design Add and Search Words","Medium"),
 (107,"Letter Combinations of Phone Number","Medium"),(108,"Generate Parentheses","Medium"),
 (109,"Combination Sum II","Medium"),(110,"Subsets II","Medium"),
 (111,"Permutations II","Medium"),(112,"Remove Nth Node From End","Medium"),
 (113,"Reorder List","Medium"),(114,"Add Two Numbers","Medium"),
 (115,"Swap Nodes in Pairs","Medium"),(116,"Reverse Nodes in k-Group","Hard"),
 (117,"Copy List with Random Pointer","Medium"),
 (118,"Longest Palindromic Substring","Medium"),(119,"Palindromic Substrings","Medium"),
 (120,"Minimum Path Sum","Medium"),(121,"Triangle","Medium"),
 (122,"Best Time to Buy Sell Stock with Cooldown","Medium"),
 (123,"Best Time to Buy Sell Stock with Transaction Fee","Medium"),
 (124,"Edit Distance","Hard"),(125,"Distinct Subsequences","Hard"),
 (126,"Interleaving String","Hard"),(127,"Maximum Profit in Job Scheduling","Hard"),
 (128,"Kth Smallest Element in BST","Medium"),
 (129,"Construct Binary Tree from Preorder and Inorder","Medium"),
 (130,"Binary Tree Right Side View","Medium"),
 (131,"Count Good Nodes in Binary Tree","Medium"),(132,"Path Sum II","Medium"),
 (133,"Populating Next Right Pointers","Medium"),
 (134,"Flatten Binary Tree to Linked List","Medium"),
 (135,"Sum Root to Leaf Numbers","Medium"),(136,"Max Area of Island","Medium"),
 (137,"Surrounded Regions","Medium"),(138,"Evaluate Division","Medium"),
 (139,"Minimum Height Trees","Medium"),(140,"Redundant Connection","Medium"),
 (141,"Number of Connected Components","Medium"),(142,"Graph Valid Tree","Medium"),
 (143,"Cheapest Flights Within K Stops","Medium"),(144,"Network Delay Time","Medium"),
 (145,"Minimum Cost to Connect All Points","Medium"),(146,"Swim in Rising Water","Hard"),
 (147,"Alien Dictionary","Hard"),(148,"First Missing Positive","Hard"),
 (149,"Trapping Rain Water II","Hard"),
 (150,"Smallest Rectangle Enclosing Black Pixels","Hard"),
 (151,"Basic Calculator","Hard"),(152,"Decode String","Medium"),
 (153,"Asteroid Collision","Medium"),(154,"Simplify Path","Medium"),
 (155,"Evaluate Reverse Polish Notation","Medium"),(156,"Car Fleet","Medium"),
 (157,"Sum of Subarray Minimums","Medium"),(158,"Online Stock Span","Medium"),
 (159,"Two Sum II","Medium"),(160,"Sort Colors","Medium"),
 (161,"Squares of Sorted Array","Easy"),(162,"Minimum Size Subarray Sum","Medium"),
 (163,"Fruit Into Baskets","Medium"),(164,"Permutation in String","Medium"),
 (165,"Find All Anagrams in a String","Medium"),(166,"Maximum Average Subarray I","Easy"),
 (167,"Longest Repeating Character Replacement","Medium"),
 (168,"Count Number of Nice Subarrays","Medium"),(169,"Sort an Array","Medium"),
 (170,"Insert Interval","Medium"),(171,"Meeting Rooms","Easy"),
 (172,"Meeting Rooms II","Medium"),(173,"Non-overlapping Intervals","Medium"),
 (174,"Minimum Number of Arrows to Burst Balloons","Medium"),
 (175,"Integer to Roman","Medium"),(176,"H-Index","Medium"),
 (177,"Candy","Hard"),(178,"Reverse Words in a String","Medium"),
 (179,"Zigzag Conversion","Medium"),(180,"Text Justification","Hard"),
 (181,"Find K Pairs with Smallest Sums","Medium"),(182,"IPO","Hard"),
 (183,"Ugly Number II","Medium"),(184,"Maximum Number of Events Attended","Medium"),
 (185,"Burst Balloons","Hard"),(186,"Palindrome Pairs","Hard"),
 (187,"Maximum Gap","Hard"),(188,"Russian Doll Envelopes","Hard"),
 (189,"Count of Smaller Numbers After Self","Hard"),(190,"Reverse Pairs","Hard"),
 (191,"Student Attendance Record II","Hard"),(192,"Strange Printer","Hard"),
 (193,"Minimum Window Subsequence","Hard"),
 (194,"Find Longest Awesome Substring","Hard"),
 (195,"Substring with Concatenation of All Words","Hard"),
]

for pid, title, diff in _EXTRA:
    PROBLEMS_DB.append({
        "id": pid, "title": title, "difficulty": diff,
        "topics": [], "acceptance": 50.0, "plans": [], "time_limit_ms": 3000,
        "test_cases": [
            {"input": "sample input", "expected_output": "sample output", "hidden": False}
        ],
    })

# O(1) lookup map
_ID_MAP: Dict[int, Dict] = {p["id"]: p for p in PROBLEMS_DB}


# ─────────────────────────────────────────────────────────────────────────────
#  SERVICE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def get_all_problems() -> List[Dict]:
    return sorted(PROBLEMS_DB, key=lambda p: p["id"])

def get_problem_by_id(problem_id: int) -> Optional[Dict]:
    return _ID_MAP.get(problem_id)

def get_problems_by_difficulty(difficulty: str) -> List[Dict]:
    return [p for p in PROBLEMS_DB if p["difficulty"].lower() == difficulty.lower()]

def get_problems_by_topic(topic: str) -> List[Dict]:
    return [p for p in PROBLEMS_DB if topic in p.get("topics", [])]

def get_problems_by_plan(plan: str) -> List[Dict]:
    return [p for p in PROBLEMS_DB if plan in p.get("plans", [])]

def search_problems(problems: List[Dict], query: str) -> List[Dict]:
    q = query.lower().strip()
    if not q:
        return problems
    return [p for p in problems
            if q in p["title"].lower()
            or any(q in t.lower() for t in p.get("topics", []))]

def get_difficulty_stats(problems: Optional[List[Dict]] = None) -> Dict:
    if problems is None:
        problems = PROBLEMS_DB
    stats: Dict[str, int] = {"Easy": 0, "Medium": 0, "Hard": 0}
    for p in problems:
        d = p.get("difficulty", "")
        if d in stats:
            stats[d] += 1
    stats["total"] = sum(stats.values())
    return stats

def get_topics_list(problems: Optional[List[Dict]] = None) -> List[Dict]:
    if problems is None:
        problems = PROBLEMS_DB
    tc: Dict[str, int] = {}
    for p in problems:
        for t in p.get("topics", []):
            tc[t] = tc.get(t, 0) + 1
    return sorted([{"topic": k, "count": v} for k, v in tc.items()],
                  key=lambda x: x["count"], reverse=True)

def get_problem_boilerplate(problem_id: int, language: str) -> str:
    p = get_problem_by_id(problem_id)
    if not p:
        return ""
    return p.get("boilerplate", {}).get(language,
        f"# {p['title']}\n# Write your solution here\npass\n")