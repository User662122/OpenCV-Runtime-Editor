package com.opencv.runtime

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val textView = TextView(this)
        textView.text = "OpenCV Runtime Editor\n\nWorking Android App!\n\nThis is a minimal working version.\nSee README.md for setup instructions."
        textView.textSize = 16f
        textView.setPadding(32, 32, 32, 32)
        
        setContentView(textView)
    }
}
