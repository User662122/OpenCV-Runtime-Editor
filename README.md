# OpenCV Runtime Code Editor for Android

A complete Android app that allows you to write and execute Kotlin code at runtime with OpenCV integration.

## Features

- 🖼️ **Image Selection**: Pick images from gallery
- 📝 **Code Editor**: Write custom Kotlin image processing code
- 🔧 **Runtime Execution**: Execute code directly on device (offline)
- 📷 **OpenCV Integration**: Full OpenCV 4.10.0 support
- 🎨 **Live Preview**: See processed images instantly
- 🔒 **Safe Execution**: Sandboxed code execution

## How to Use

### 1. Import to Android Studio

1. Download/clone this project
2. Open Android Studio
3. Select **File > Open** and choose this project folder
4. Wait for Gradle sync to complete
5. Connect your Android device or start an emulator
6. Click **Run** (▶️) button

### 2. Using the App

1. **Select Image**: Tap "Select Image" to choose a photo from gallery
2. **Write Code**: Use the code editor to write your OpenCV processing function
3. **Execute**: Tap "Execute Code" to run your code
4. **View Result**: See the processed image in the output view

### 3. Code Structure

Your code must contain a function with this signature:

```kotlin
fun process(bitmap: Bitmap): Bitmap {
    // Your OpenCV code here
    return processedBitmap
}
```

## Sample Codes

### Grayscale Conversion
```kotlin
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
```

### Gaussian Blur
```kotlin
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
```

### Edge Detection (Canny)
```kotlin
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
```

## Requirements

- **Android SDK**: Minimum API 24 (Android 7.0)
- **Target SDK**: API 34
- **OpenCV**: 4.10.0 (from Maven)
- **Kotlin**: 1.9.20

## Permissions

The app requires:
- `READ_EXTERNAL_STORAGE` - To select images from gallery
- `READ_MEDIA_IMAGES` - For Android 13+ image access
- `CAMERA` - Optional, for camera features (not currently used)

## Dependencies

- **AndroidX Core KTX**: 1.12.0
- **Material Design**: 1.11.0
- **OpenCV Android**: 4.10.0
- **Sora Code Editor**: 0.23.2 (for code editing UI)
- **Kotlin Scripting**: 1.9.20 (for runtime execution)

## How It Works

1. **Image Selection**: User picks an image from device gallery
2. **Code Input**: User writes Kotlin code in the editor
3. **Code Analysis**: The executor parses and validates the code
4. **Safe Execution**: Code runs in a controlled environment
5. **OpenCV Processing**: Image is processed using OpenCV functions
6. **Result Display**: Processed image is shown to the user

## Security

The app uses pattern matching and controlled execution to prevent:
- File system access
- Network operations
- Dangerous system calls
- Infinite loops (timeout protection)

## Troubleshooting

### OpenCV Initialization Failed
- Make sure OpenCV library is properly loaded
- Check that the app has proper permissions

### Image Not Loading
- Grant storage permissions in device settings
- Ensure image format is supported (JPG, PNG)

### Code Execution Failed
- Verify code syntax is correct
- Ensure the `process()` function signature matches
- Check console output for error details

## Project Structure

```
app/
├── src/main/
│   ├── java/com/opencv/runtime/
│   │   ├── MainActivity.kt           # Main activity
│   │   ├── KotlinScriptExecutor.kt   # Runtime code execution
│   │   └── SampleCodes.kt            # Sample code templates
│   ├── res/
│   │   └── layout/
│   │       └── activity_main.xml     # UI layout
│   └── AndroidManifest.xml
└── build.gradle.kts
```

## License

This project is provided as-is for educational purposes.

## Notes

- This app runs **100% offline** - no server required
- OpenCV library is loaded from Maven (4.10.0)
- Code execution is pattern-based for safety
- Suitable for learning OpenCV and image processing
