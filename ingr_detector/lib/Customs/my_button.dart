import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:ingr_detector/pages/result.dart';

class UploadButton extends StatefulWidget {
  const UploadButton({Key? key}) : super(key: key);

  @override
  State<UploadButton> createState() => _UploadButtonState();
}

class _UploadButtonState extends State<UploadButton> {
  final ImagePicker _picker = ImagePicker();
  bool _loading = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.brown[100],
        borderRadius: BorderRadius.circular(4),
      ),
      child: Column(
        children: [
          ListTile(
            title: const Text("Upload"),
            subtitle: const Text("click to open gallery"),
            leading: Image.asset("lib/images/chai.png"),
            trailing: const Icon(Icons.upload),
            onTap: () => getImageFromGallery(),
          ),
          const SizedBox(height: 10),
          ListTile(
            title: const Text("Capture"),
            subtitle: const Text("click to capture image"),
            leading: Image.asset("lib/images/coffee.png"),
            trailing: const Icon(Icons.camera_alt),
            onTap: () => getImageFromCamera(),
          ),
          Visibility(
            visible: _loading,
            child: Container(
              color: Colors.transparent,
              child: const Center(
                child: CircularProgressIndicator(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future getImageFromGallery() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      uploadAndNavigate(image);
    }
  }

  Future getImageFromCamera() async {
    final XFile? image = await _picker.pickImage(source: ImageSource.camera);
    if (image != null) {
      uploadAndNavigate(image);
    }
  }

  Future<void> uploadAndNavigate(XFile image) async {
    setState(() {
      _loading = true;
    });
    bool uploaded = await uploadImage(image);
    setState(() {
      _loading = false;
    });
    if (uploaded) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => const Myresults()),
      );
    }
  }

  Future<bool> uploadImage(XFile image) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('http://172.20.203.123:5000/upload'),
      );
      request.files.add(await http.MultipartFile.fromPath('image', image.path));
      var response = await request.send();

      if (response.statusCode == 200) {
        return true;
      } else {
        print('Failed to upload image: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      print('Error uploading image: $e');
      return false;
    }
  }
}

class NewPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('New Page'),
      ),
      body: const Center(
        child: Text('You have successfully uploaded an image!'),
      ),
    );
  }
}
