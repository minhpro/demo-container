package com.example.democontainer;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class
TestController {

    @GetMapping("/greet")
    public Greet greet() {
        return new Greet("Hello");
    }

    @GetMapping("/heavy-greet")
    public Greet heavyGreet() throws InterruptedException {
        Thread.sleep(20000);
        return new Greet("Heavy Hello");
    }
}
