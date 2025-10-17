package com.example.krishirakshak.data

import android.graphics.Bitmap

data class ChatMessage(
    val text: String,
    val isFromUser: Boolean,
    val image: Bitmap? = null
)