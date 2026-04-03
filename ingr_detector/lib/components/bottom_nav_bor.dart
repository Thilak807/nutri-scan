import 'package:flutter/material.dart';
import 'package:google_nav_bar/google_nav_bar.dart';

class MyBottomNavBar extends StatelessWidget {
  const MyBottomNavBar({super.key});

  @override
  Widget build(BuildContext context) {
    return const GNav(
      mainAxisAlignment: MainAxisAlignment.center,
      tabs: [
        GButton(
          iconActiveColor: Colors.amber,
          icon: Icons.local_pizza,
          text: "Home",
          textColor: Colors.white,
        ),
      ],
    );
  }
}
