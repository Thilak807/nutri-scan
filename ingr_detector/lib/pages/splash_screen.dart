import 'dart:async';
import 'package:flutter/material.dart';
import 'package:ingr_detector/pages/home_page.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  _SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    // Navigate to the main screen after a delay
    Timer(const Duration(seconds: 2), () {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const HomePage()),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.brown,
      body: Center(
        // Replace this with your splash screen image or animation
        child: Column(children: [
          Image.asset('lib/images/chai.png'),
          const Text(
            'NutriScan',
            style: TextStyle(
              fontSize: 50,
              fontStyle: FontStyle.normal,
              color: Colors.white,
              fontWeight: FontWeight.w900,
            ),
          ),
        ]),
      ),
    );
  }
}

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Your App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const SplashScreen(), // Set the splash screen as the home screen
    );
  }
}
