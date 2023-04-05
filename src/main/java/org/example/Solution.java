package org.example;

import java.util.HashMap;

public class Solution {
    public int lengthOfLongestSubstring(String s) {
//        new AnnotationConfigApplicationContext();
//        new GenericApplicationContext();
//        new ConfigurationClassPostProcessor();
                
        HashMap<Character, Integer> map = new HashMap<>();
        if (s.length() ==0 ) return 0;
        int left =0;
        int res = 0;
        for (int i = 0; i < s.length(); i++) {
            if (map.containsKey(s.charAt(i))){
                left =Math.max(left,map.get(s.charAt(i))+1);
            }
            map.put(s.charAt(i),i);
            res = Math.max(res,i-left+1);
        }
        return res;
    }
    public String longestPalindrome(String s) {
        String res="";
        for (int i = 1; i < s.length(); i++) {
            int pre = i-1;
            int next = i+1;
            while (s.charAt(pre) ==s.charAt(next) &&pre>0 &&next<s.length()-1){
                pre--;
                next++;
            }
            if (next-pre >res.length())  res = s.substring(pre,next);
        }
        return res;
    }
}