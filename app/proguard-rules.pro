# Add project specific ProGuard rules here.
-keep class org.opencv.** { *; }
-keep class com.opencv.runtime.** { *; }
-keepclassmembers class * {
    public <init>(...);
}
