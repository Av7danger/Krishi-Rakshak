package com.example.krishirakshak.data

import android.graphics.Bitmap
import com.google.ai.client.generativeai.GenerativeModel
import com.google.ai.client.generativeai.type.content

class GeminiRepository(apiKey: String) {
    private val generativeModel = GenerativeModel(
        modelName = "gemini-pro-vision",
        apiKey = apiKey
    )

    suspend fun getResponse(prompt: String, image: Bitmap? = null): String {
        val inputContent = content {
            image?.let { image(it) }
            text(prompt)
        }

        val response = generativeModel.generateContent(inputContent)
        return response.text ?: ""
    }
}