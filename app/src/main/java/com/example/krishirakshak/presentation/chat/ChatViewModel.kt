package com.example.krishirakshak.presentation.chat

import android.graphics.Bitmap
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.krishirakshak.data.ChatMessage
import com.example.krishirakshak.data.GeminiRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ChatViewModel : ViewModel() {
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages = _messages.asStateFlow()

    private val geminiRepository = GeminiRepository(apiKey = "YOUR_API_KEY") // TODO: Replace with your API key

    fun sendMessage(text: String, image: Bitmap? = null) {
        addMessage(text, true, image)

        viewModelScope.launch {
            val response = geminiRepository.getResponse(text, image)
            addMessage(response, false)
        }
    }

    private fun addMessage(text: String, isFromUser: Boolean, image: Bitmap? = null) {
        _messages.value = _messages.value + ChatMessage(text, isFromUser, image)
    }
}