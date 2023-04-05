package org.example;

import java.math.BigDecimal;
import java.util.*;

public class Main {
    static int count =0;

    public static void main(String[] args) {
        ArrayList<ArrayList<String>> res = new ArrayList<>();
        ArrayList<String> integers = new ArrayList<>();
        Scanner scanner = new Scanner(System.in);
        int n = scanner.nextInt();
        for (int i = 0; i < n-1; i++) {
            integers.add(scanner.next());
            integers.add("+");
        }
        integers.add(scanner.next());
        int i = 2*scanner.nextInt();
        ArrayList<String> strings = new ArrayList<>();
        for (int i1 = 0; i1 < i; i1++) {
            strings.add(scanner.next());
        }
        HashMap<Integer, String> map = new HashMap<>();
        for (int i1 = 0; i1 < strings.size();) {
            map.put(Integer.valueOf(strings.get(i1)),strings.get(i1+1));
            i1 = i1+2;
        }
        Stack<String> stack = new Stack<>();
        
        map.entrySet().forEach((integerStringEntry -> {
            ArrayList<String> temp = (ArrayList<String>) integers.clone();
            temp.set(integerStringEntry.getKey()*2-1,integerStringEntry.getValue());
            for (int i1 = 0; i1 < temp.size(); i1++) {
                stack.push(temp.get(i1));
            }
            if (count<=map.size()-2){
                count++;
                System.out.print(String.format("%.1f",Double.valueOf(calculate(stack)))+" ");
            }else
                System.out.println(String.format("%.1f",Double.valueOf(calculate(stack))));
        }));
    }
    public static String calculate(Stack<String> s){
        ArrayList<String> strings = new ArrayList<>();
        
        while (!s.isEmpty()){
            if ("*".equals(s.peek())||"/".equals(s.peek())){
                String f = s.pop();
                String n = s.pop();
                String last = strings.remove(strings.size()-1);
                if (f.equals("*")){
                    strings.add(new BigDecimal(last).multiply(new BigDecimal(n)).toString());
                }
                else {
                    
                    strings.add(new BigDecimal(n).divide(new BigDecimal(last)).toString());
                }
            }else {
                strings.add(s.pop());
            }
        }
        BigDecimal b = new BigDecimal(strings.remove(0));
        
        for (int i = 0; i < strings.size(); i++) {
            if (strings.get(i).equals("-")){
                String temp1 ="";
                String temp2 = "";
                temp1 =strings.get(i+1);
                temp2 = strings.get(i-1);
                strings.set(i-1,temp1);
                strings.set(i+1,temp2);
            }
        }
        Iterator<String> iterator = strings.iterator();
        while (iterator.hasNext()){
            String next = iterator.next();
            if (next.equals("+")){
                b = b.add(new BigDecimal(iterator.next()));
            }else if (next.equals("-")){
                b = b.subtract(new BigDecimal(iterator.next()));
            }
        }
        return b.toString();
    }
}
