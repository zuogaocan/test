package org.example;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class user implements Comparable<user>{
    private int age;

    @Override
    public int compareTo(user o) {
        return this.age-o.getAge();
    }
}
