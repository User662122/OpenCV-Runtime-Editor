package com.opencv.runtime

import android.graphics.Bitmap
import android.graphics.ColorMatrix
import android.graphics.ColorMatrixColorFilter
import android.graphics.Canvas
import android.graphics.Paint

object SimpleImageProcessor {
    
    fun processImage(bitmap: Bitmap, code: String): Bitmap {
        return when {
            code.contains("grayscale", ignoreCase = true) || 
            code.contains("COLOR_BGR2GRAY", ignoreCase = true) -> {
                toGrayscale(bitmap)
            }
            code.contains("blur", ignoreCase = true) || 
            code.contains("GaussianBlur", ignoreCase = true) -> {
                applyBlur(bitmap)
            }
            code.contains("brightness", ignoreCase = true) -> {
                adjustBrightness(bitmap, 1.5f)
            }
            code.contains("contrast", ignoreCase = true) -> {
                adjustContrast(bitmap, 1.5f)
            }
            code.contains("invert", ignoreCase = true) -> {
                invertColors(bitmap)
            }
            else -> {
                // Return original if no matching operation
                bitmap.copy(bitmap.config, true)
            }
        }
    }
    
    private fun toGrayscale(bitmap: Bitmap): Bitmap {
        val result = Bitmap.createBitmap(bitmap.width, bitmap.height, bitmap.config)
        val canvas = Canvas(result)
        val paint = Paint()
        val colorMatrix = ColorMatrix()
        colorMatrix.setSaturation(0f)
        paint.colorFilter = ColorMatrixColorFilter(colorMatrix)
        canvas.drawBitmap(bitmap, 0f, 0f, paint)
        return result
    }
    
    private fun applyBlur(bitmap: Bitmap): Bitmap {
        // Simple box blur implementation
        val result = Bitmap.createBitmap(bitmap.width, bitmap.height, bitmap.config)
        val width = bitmap.width
        val height = bitmap.height
        val radius = 5
        
        for (y in 0 until height) {
            for (x in 0 until width) {
                var r = 0
                var g = 0
                var b = 0
                var count = 0
                
                for (dy in -radius..radius) {
                    for (dx in -radius..radius) {
                        val nx = (x + dx).coerceIn(0, width - 1)
                        val ny = (y + dy).coerceIn(0, height - 1)
                        val pixel = bitmap.getPixel(nx, ny)
                        r += android.graphics.Color.red(pixel)
                        g += android.graphics.Color.green(pixel)
                        b += android.graphics.Color.blue(pixel)
                        count++
                    }
                }
                
                val color = android.graphics.Color.rgb(r / count, g / count, b / count)
                result.setPixel(x, y, color)
            }
        }
        
        return result
    }
    
    private fun adjustBrightness(bitmap: Bitmap, factor: Float): Bitmap {
        val result = Bitmap.createBitmap(bitmap.width, bitmap.height, bitmap.config)
        val canvas = Canvas(result)
        val paint = Paint()
        val colorMatrix = ColorMatrix(floatArrayOf(
            factor, 0f, 0f, 0f, 0f,
            0f, factor, 0f, 0f, 0f,
            0f, 0f, factor, 0f, 0f,
            0f, 0f, 0f, 1f, 0f
        ))
        paint.colorFilter = ColorMatrixColorFilter(colorMatrix)
        canvas.drawBitmap(bitmap, 0f, 0f, paint)
        return result
    }
    
    private fun adjustContrast(bitmap: Bitmap, contrast: Float): Bitmap {
        val result = Bitmap.createBitmap(bitmap.width, bitmap.height, bitmap.config)
        val canvas = Canvas(result)
        val paint = Paint()
        val scale = contrast
        val translate = (-.5f * scale + .5f) * 255f
        val colorMatrix = ColorMatrix(floatArrayOf(
            scale, 0f, 0f, 0f, translate,
            0f, scale, 0f, 0f, translate,
            0f, 0f, scale, 0f, translate,
            0f, 0f, 0f, 1f, 0f
        ))
        paint.colorFilter = ColorMatrixColorFilter(colorMatrix)
        canvas.drawBitmap(bitmap, 0f, 0f, paint)
        return result
    }
    
    private fun invertColors(bitmap: Bitmap): Bitmap {
        val result = Bitmap.createBitmap(bitmap.width, bitmap.height, bitmap.config)
        val canvas = Canvas(result)
        val paint = Paint()
        val colorMatrix = ColorMatrix(floatArrayOf(
            -1f, 0f, 0f, 0f, 255f,
            0f, -1f, 0f, 0f, 255f,
            0f, 0f, -1f, 0f, 255f,
            0f, 0f, 0f, 1f, 0f
        ))
        paint.colorFilter = ColorMatrixColorFilter(colorMatrix)
        canvas.drawBitmap(bitmap, 0f, 0f, paint)
        return result
    }
}
