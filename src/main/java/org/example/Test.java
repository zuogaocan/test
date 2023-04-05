package org.example;

import java.util.Scanner;
import java.util.Stack;

public class Test {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        String next = in.next();
        if (right(next)){
            for (int i = 0; i < next.length(); i++) {
                if (next.charAt(i) =='{' ||next.charAt(i) =='}'){
                    System.out.print("红");
                }else if (next.charAt(i) =='[' ||next.charAt(i) ==']'){
                    System.out.print("黄");
                }else {
                    System.out.print("蓝");
                }
            }
        }
        else {
            System.out.println("输入错误");
        }

    }

    private static boolean right(String s) {
        if (s ==null) return false;
        if (s.length() ==0) return false;
        Stack<Character> stack = new Stack<>();
        for (int i = 0; i < s.length(); i++) {
            char c =s.charAt(i);
            if (c=='{' || c =='[' ||c=='('){
                stack.push(c);
            }else {
                if (stack.isEmpty()){
                    return false;
                }
                char temp = stack.peek();
                if (temp =='{' && c =='}'|| temp =='[' && c ==']' ||temp =='(' && c ==')'){
                    stack.pop();
                }else {
                    return false;
                }
            }
        }
        if (!stack.isEmpty()) return false;
        return true;
    }
}
