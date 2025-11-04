package com.opencv.runtime

object SampleCodes {
    
    val GRAYSCALE = """
// Grayscale Conversion
import org.opencv.core.*
import org.opencv.imgproc.Imgproc
import android.graphics.Bitmap

fun process(bitmap: Bitmap): Bitmap {
    val src = Mat()
    Utils.bitmapToMat(bitmap, src)
    
    val gray = Mat()
    Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY)
    
    val result = Bitmap.createBitmap(
        gray.cols(), gray.rows(), Bitmap.Config.ARGB_8888
    )
    Utils.matToBitmap(gray, result)
    
    return result
}
    """.trimIndent()

    val GAUSSIAN_BLUR = """
// Gaussian Blur Effect
import org.opencv.core.*
import org.opencv.imgproc.Imgproc
import android.graphics.Bitmap

fun process(bitmap: Bitmap): Bitmap {
    val src = Mat()
    Utils.bitmapToMat(bitmap, src)
    
    val blurred = Mat()
    Imgproc.GaussianBlur(src, blurred, Size(15.0, 15.0), 0.0)
    
    val result = Bitmap.createBitmap(
        blurred.cols(), blurred.rows(), Bitmap.Config.ARGB_8888
    )
    Utils.matToBitmap(blurred, result)
    
    return result
}
    """.trimIndent()

    val CANNY_EDGES = """
// Canny Edge Detection
import org.opencv.core.*
import org.opencv.imgproc.Imgproc
import android.graphics.Bitmap

fun process(bitmap: Bitmap): Bitmap {
    val src = Mat()
    Utils.bitmapToMat(bitmap, src)
    
    val gray = Mat()
    Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY)
    
    val edges = Mat()
    Imgproc.Canny(gray, edges, 50.0, 150.0)
    
    val result = Bitmap.createBitmap(
        edges.cols(), edges.rows(), Bitmap.Config.ARGB_8888
    )
    Utils.matToBitmap(edges, result)
    
    return result
}
    """.trimIndent()

    val THRESHOLD = """
// Binary Threshold
import org.opencv.core.*
import org.opencv.imgproc.Imgproc
import android.graphics.Bitmap

fun process(bitmap: Bitmap): Bitmap {
    val src = Mat()
    Utils.bitmapToMat(bitmap, src)
    
    val gray = Mat()
    Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY)
    
    val thresh = Mat()
    Imgproc.threshold(gray, thresh, 127.0, 255.0, Imgproc.THRESH_BINARY)
    
    val result = Bitmap.createBitmap(
        thresh.cols(), thresh.rows(), Bitmap.Config.ARGB_8888
    )
    Utils.matToBitmap(thresh, result)
    
    return result
}
    """.trimIndent()

    val FIND_CONTOURS = """
// Find and Draw Contours
import org.opencv.core.*
import org.opencv.imgproc.Imgproc
import android.graphics.Bitmap

fun process(bitmap: Bitmap): Bitmap {
    val src = Mat()
    Utils.bitmapToMat(bitmap, src)
    
    val gray = Mat()
    Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY)
    
    val edges = Mat()
    Imgproc.Canny(gray, edges, 50.0, 150.0)
    
    val contours = mutableListOf<MatOfPoint>()
    val hierarchy = Mat()
    Imgproc.findContours(
        edges, contours, hierarchy,
        Imgproc.RETR_EXTERNAL,
        Imgproc.CHAIN_APPROX_SIMPLE
    )
    
    val output = src.clone()
    Imgproc.drawContours(output, contours, -1, Scalar(0.0, 255.0, 0.0), 2)
    
    val result = Bitmap.createBitmap(
        output.cols(), output.rows(), Bitmap.Config.ARGB_8888
    )
    Utils.matToBitmap(output, result)
    
    return result
}
    """.trimIndent()
}
