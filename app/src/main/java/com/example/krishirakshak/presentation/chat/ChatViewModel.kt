package com.example.krishirakshak.presentation.chat

import android.graphics.Bitmap
import androidx.lifecycle.ViewModel
import com.example.krishirakshak.data.ChatMessage
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

class ChatViewModel : ViewModel() {
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages = _messages.asStateFlow()

    fun addMessage(text: String, isFromUser: Boolean, image: Bitmap? = null) {
        _messages.value = _messages.value + ChatMessage(text, isFromUser, image)
    }
}