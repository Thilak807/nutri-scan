import 'package:flutter/material.dart';
import 'package:ingr_detector/Customs/my_button.dart';
import 'package:ingr_detector/components/bottom_nav_bor.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.brown[300],
      bottomNavigationBar: const MyBottomNavBar(),
      body: Padding(
        padding: const EdgeInsets.all(30),
        child: SafeArea(
          child: Container(
            child: SingleChildScrollView(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  SizedBox(height: MediaQuery.of(context).size.height * 0.3),
                  const Text(
                    'NutriScan',
                    style: TextStyle(
                      fontSize: 50,
                      fontStyle: FontStyle.normal,
                      color: Colors.white,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const UploadButton(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
