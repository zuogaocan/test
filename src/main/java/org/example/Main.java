package org.example;

import java.util.*;
import java.util.logging.Logger;

/**
 * Hello world!
 *
 */

public class Main {
    private static final Logger logger = Logger.getLogger(SGVA.class.getName());

    public static int count = 0;
    public static void main(String[] args) {

        Scanner scanner = new Scanner(System.in);
        String input = scanner.next();
        String[] inputs = input.split(",");
        int num = Integer.parseInt(inputs[0]);
        int times = Integer.parseInt(inputs[1]);
        int sum = 0;

        logger.info("Calculating the sum of " + num + " and its concatenations for " + times + " times.");
        for (int i = 1; i <= times; i++) {
            sum += num;
            num = Integer.parseInt(num + inputs[0]);
            logger.info("The " + i + "th number is " + num);
        }
        logger.info("The final sum is " + sum);
    }
    public static void func(char[] chars , int i, ArrayList<Character> list){
        if (i == chars.length){
            count++;
            System.out.print(list.toString());
            return;
        }
        ArrayList list1 = (ArrayList) list.clone();
        list1.add(chars[i]);
        func(chars,i+1,list1);
        ArrayList list2 = (ArrayList) list.clone();
        func(chars,i+1,list2);
    }
    public static void func2(char[] chars,int i, ArrayList<String> list){
        if (i ==chars.length) {
            list.add(String.valueOf(chars));
        }
        for (int j=i; j<chars.length;j++){
            swap(chars,i,j);
            func2(chars,i+1,list);
            swap(chars,i,j);
        }
    }

    private static void swap(char[] chars, int i, int j) {
        char temp = chars[i];
        chars[i] = chars[j];
        chars[j] = temp;
    }
    
    
    
    //多少条路径
    public int uniquePaths(int m, int n) {
        int[][] map = new int[m][n];
        return function(map,0,0,m,n);
    }
    private int function(int[][] map, int i, int j, int m, int n) {
        if (map[i][j] !=0)
            return map[i][j];
        if (i ==m-1 ||j==n-1) return 1;
        return map[i][j] =function(map,i + 1, j, m, n) + function(map, i, j + 1, m, n);
    }

    public int[][] merge(int[][] intervals) {
        if (intervals.length==0) return new int[0][];
        sorted(intervals,0,intervals.length-1);
        int j =0;
        for (int i = 1; i < intervals.length; i++) {
            if (intervals[j][1]>= intervals[i][0]){
                intervals[j][1] = Math.max(intervals[j][1],intervals[i][1]);
            }
            else {
                j++;
                intervals[j] =intervals[i];
            }
        }
        return Arrays.copyOf(intervals,j+1);
    }
    private void sorted(int[][] intervals,int left,int right) {
        if (left>=right) return;
        
        int[] r =intervals[right];
        int index = left;
        for (int i = left; i < right; i++) {
            if (intervals[i][0] < r[0]){
                int[] temp = intervals[index];
                intervals[index] = intervals[i];
                intervals[i] = temp;
                index++;
            }
        }
        intervals[right] =intervals[index];
        intervals[index] = r;
        sorted(intervals,left,index-1);
        sorted(intervals,index+1,right);
    }
}