plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.opencv.runtime"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.opencv.runtime"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // OpenCV
    implementation("org.opencv:opencv:4.10.0")
    
    // Kotlin scripting
    implementation("org.jetbrains.kotlin:kotlin-scripting-jvm:1.9.20")
    implementation("org.jetbrains.kotlin:kotlin-script-runtime:1.9.20")
    implementation("org.jetbrains.kotlin:kotlin-compiler-embeddable:1.9.20")
    implementation("org.jetbrains.kotlin:kotlin-scripting-compiler-embeddable:1.9.20")
    
    // Code editor
    implementation("io.github.rosemoe.sora-editor:editor:0.23.2")
    implementation("io.github.rosemoe.sora-editor:language-textmate:0.23.2")
}
