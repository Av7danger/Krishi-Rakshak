package com.example.krishirakshak.presentation

import android.graphics.ImageDecoder
import android.net.Uri
import android.os.Build
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AddAPhoto
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.example.krishirakshak.data.ChatMessage
import com.example.krishirakshak.presentation.chat.ChatViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(navController: NavController, viewModel: ChatViewModel = viewModel()) {
    val messages by viewModel.messages.collectAsState()
    val context = LocalContext.current

    LaunchedEffect(navController.currentBackStackEntry) {
        val uri = navController.currentBackStackEntry?.savedStateHandle?.get<Uri>("captured_image_uri")
        uri?.let {
            val source = ImageDecoder.createSource(context.contentResolver, it)
            val bitmap = ImageDecoder.decodeBitmap(source)
            viewModel.addMessage("", true, bitmap)
            navController.currentBackStackEntry?.savedStateHandle?.remove<Uri>("captured_image_uri")
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("KrishiRakshak") })
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            LazyColumn(
                modifier = Modifier.weight(1f),
                contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp)
            ) {
                items(messages) { message ->
                    ChatMessageItem(message = message)
                }
            }
            InputBar(
                onPhotoClick = { navController.navigate("camera") },
                onSendClick = { text -> viewModel.addMessage(text, true) }
            )
        }
    }
}

@Composable
fun ChatMessageItem(message: ChatMessage) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalAlignment = if (message.isFromUser) Alignment.End else Alignment.Start
    ) {
        Surface(
            shape = MaterialTheme.shapes.medium,
            tonalElevation = 2.dp,
            modifier = Modifier.padding(horizontal = 8.dp)
        ) {
            Column(modifier = Modifier.padding(12.dp)) {
                message.image?.let {
                    Image(
                        bitmap = it.asImageBitmap(),
                        contentDescription = null, // decorative
                        modifier = Modifier.size(200.dp)
                    )
                }
                if (message.text.isNotEmpty()) {
                    Text(text = message.text)
                }
            }
        }
    }
}

@Composable
fun InputBar(onPhotoClick: () -> Unit, onSendClick: (String) -> Unit) {
    var text by remember { mutableStateOf("") }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        IconButton(onClick = onPhotoClick) {
            Icon(Icons.Default.AddAPhoto, contentDescription = "Add photo")
        }
        OutlinedTextField(
            value = text,
            onValueChange = { text = it },
            modifier = Modifier.weight(1f),
            placeholder = { Text("Type a message...") }
        )
        IconButton(onClick = {
            onSendClick(text)
            text = ""
        }) {
            Icon(Icons.Default.Send, contentDescription = "Send message")
        }
    }
}