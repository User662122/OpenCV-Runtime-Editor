package com.opencv.runtime

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.io.InputStream

class MainActivity : AppCompatActivity() {

    private lateinit var btnSelectImage: Button
    private lateinit var btnLoadSample: Button
    private lateinit var btnExecute: Button
    private lateinit var ivSelectedImage: ImageView
    private lateinit var ivProcessedImage: ImageView
    private lateinit var codeEditor: EditText
    private lateinit var tvConsole: TextView

    private var selectedBitmap: Bitmap? = null
    private val PICK_IMAGE_REQUEST = 1
    private val PERMISSION_REQUEST_CODE = 100

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        log("Android Image Processor initialized!")
        
        initViews()
        setupListeners()
        loadDefaultCode()
        requestPermissions()
    }

    private fun initViews() {
        btnSelectImage = findViewById(R.id.btnSelectImage)
        btnLoadSample = findViewById(R.id.btnLoadSample)
        btnExecute = findViewById(R.id.btnExecute)
        ivSelectedImage = findViewById(R.id.ivSelectedImage)
        ivProcessedImage = findViewById(R.id.ivProcessedImage)
        codeEditor = findViewById(R.id.codeEditor)
        tvConsole = findViewById(R.id.tvConsole)
    }

    private fun setupListeners() {
        btnSelectImage.setOnClickListener {
            selectImage()
        }

        btnLoadSample.setOnClickListener {
            loadDefaultCode()
        }

        btnExecute.setOnClickListener {
            executeCode()
        }
    }

    private fun requestPermissions() {
        val permissions = arrayOf(
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.READ_MEDIA_IMAGES
        )

        val permissionsToRequest = permissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }

        if (permissionsToRequest.isNotEmpty()) {
            ActivityCompat.requestPermissions(
                this,
                permissionsToRequest.toTypedArray(),
                PERMISSION_REQUEST_CODE
            )
        }
    }

    private fun selectImage() {
        val intent = Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
        startActivityForResult(intent, PICK_IMAGE_REQUEST)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        if (requestCode == PICK_IMAGE_REQUEST && resultCode == RESULT_OK && data != null) {
            val imageUri: Uri? = data.data
            try {
                val inputStream: InputStream? = imageUri?.let { contentResolver.openInputStream(it) }
                selectedBitmap = BitmapFactory.decodeStream(inputStream)
                ivSelectedImage.setImageBitmap(selectedBitmap)
                log("Image loaded successfully!")
            } catch (e: Exception) {
                log("Error loading image: ${e.message}")
                Toast.makeText(this, "Failed to load image", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun loadDefaultCode() {
        val sampleCode = """
// Grayscale Conversion
// Keywords: grayscale, COLOR_BGR2GRAY

fun process(bitmap: Bitmap): Bitmap {
    // Convert image to grayscale
    return grayscale(bitmap)
}

// Available operations:
// - grayscale
// - blur
// - brightness
// - contrast
// - invert
        """.trimIndent()
        
        codeEditor.setText(sampleCode)
        log("Sample code loaded. Select an image and click Execute!")
    }

    private fun executeCode() {
        if (selectedBitmap == null) {
            log("ERROR: Please select an image first!")
            Toast.makeText(this, "Please select an image first", Toast.LENGTH_SHORT).show()
            return
        }

        val code = codeEditor.text.toString()
        if (code.isBlank()) {
            log("ERROR: Code editor is empty!")
            return
        }

        log("Executing code...")
        
        try {
            val result = SimpleImageProcessor.processImage(selectedBitmap!!, code)
            ivProcessedImage.setImageBitmap(result)
            log("✓ Code executed successfully!")
        } catch (e: Exception) {
            log("ERROR: ${e.message}")
            e.printStackTrace()
            Toast.makeText(this, "Execution failed: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    private fun log(message: String) {
        runOnUiThread {
            val currentText = tvConsole.text.toString()
            val newText = if (currentText == "Console output will appear here...") {
                message
            } else {
                "$currentText\n$message"
            }
            tvConsole.text = newText
        }
    }
}
