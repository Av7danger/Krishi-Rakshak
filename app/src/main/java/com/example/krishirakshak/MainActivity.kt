package com.example.krishirakshak

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.krishirakshak.presentation.ChatScreen
import com.example.krishirakshak.presentation.camera.CameraScreen
import com.example.krishirakshak.ui.theme.KrishiRakshakTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            KrishiRakshakTheme {
                KrishiRakshakApp()
            }
        }
    }
}

@Composable
fun KrishiRakshakApp() {
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = "chat") {
        composable("chat") {
            ChatScreen(navController = navController)
        }
        composable("camera") {
            CameraScreen(onImageCaptured = {
                navController.previousBackStackEntry
                    ?.savedStateHandle
                    ?.set("captured_image_uri", it)
                navController.popBackStack()
            })
        }
    }
}