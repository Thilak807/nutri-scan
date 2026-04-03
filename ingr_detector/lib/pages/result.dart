import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class Myresults extends StatefulWidget {
  const Myresults({Key? key}) : super(key: key);

  @override
  State<Myresults> createState() => _MyresultsState();
}

class _MyresultsState extends State<Myresults> {
  String? _result;
  bool _isLoading = false;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    fetchData();
  }

  Future<void> fetchData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final response =
          await http.get(Uri.parse('http://172.20.203.123:5000/get'));
      if (response.statusCode == 200) {
        setState(() {
          _result = response.body;
        });
      } else {
        setState(() {
          _errorMessage = 'Failed to fetch data: ${response.statusCode}';
        });
        // ignore: avoid_print
        print(_errorMessage);
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error fetching data: $e';
      });
      // ignore: avoid_print
      print(_errorMessage);
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Results'),
        backgroundColor: Colors.brown[200],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : _errorMessage.isNotEmpty
              ? Center(
                  child: Text(
                    _errorMessage,
                    style: const TextStyle(fontSize: 16),
                  ),
                )
              : _result != null
                  ? Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: SingleChildScrollView(
                        child: Text(
                          _result!,
                          style: const TextStyle(fontSize: 16),
                        ),
                      ),
                    )
                  : const Center(
                      child: Text(
                        'No data available',
                        style: TextStyle(fontSize: 16),
                      ),
                    ),
    );
  }
}
