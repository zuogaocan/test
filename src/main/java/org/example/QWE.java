package org.example;

import java.util.*;

public class QWE {
    public static void main(String[] args) {
        System.out.println(countSubStr("dsad"));
    }
    public static int countSubStr (String s) {
        HashSet<String> res = new HashSet<>();
        // write code here
        Scanner in = new Scanner(System.in);
        String next = in.next();
        next = next.substring(1,next.length()-1);
        HashSet<String> set = new HashSet<>();
        for (int i = 0; i < next.length(); i++) {
            for (int j = i+1; j <= next.length(); j++) {
                set.add(next.substring(i,j));
            }
        }
        Iterator<String> iterator = set.iterator();
        while (iterator.hasNext()){
            String temp = iterator.next();
            System.out.println(temp);
            System.out.println("==========================");
            int key_count =0;
            int max= 0;
            HashMap<Character, Integer> map = new HashMap<>();
            for (int i = 0; i < temp.length(); i++) {
                char c = temp.charAt(i);
                if (map.containsKey(c)){
                    map.put(c,map.get(c)+1);
                    max =Math.max(max,map.get(c));
                }else {
                    map.put(c,1);
                    max =Math.max(max,map.get(c));

                }
            }
            key_count =map.keySet().size();
            if (max <key_count){
                res.add(temp);
            }
            map.entrySet().forEach(entry ->{
                System.out.println(entry.getKey()+ " "+entry.getValue());
                

            });
            System.out.println();
            
        }
        System.out.println(res);
        return res.size();
    }

}
