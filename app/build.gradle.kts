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
    
    // OpenCV - Official Maven Central package
    implementation("org.opencv:opencv:4.9.0")
    
    // Kotlin scripting dependencies
    implementation("org.jetbrains.kotlin:kotlin-scripting-jsr223:1.9.20")
    implementation("org.jetbrains.kotlin:kotlin-script-runtime:1.9.20")
    implementation("org.jetbrains.kotlin:kotlin-compiler-embeddable:1.9.20")
}
