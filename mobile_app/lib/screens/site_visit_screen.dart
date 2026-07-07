import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';

import '../services/attendance_service.dart';
import '../utils/api_exception.dart';

class SiteVisitScreen extends StatefulWidget {
  final AttendanceService attendanceService;

  const SiteVisitScreen({super.key, required this.attendanceService});

  @override
  State<SiteVisitScreen> createState() => _SiteVisitScreenState();
}

class _SiteVisitScreenState extends State<SiteVisitScreen> {
  final TextEditingController _clientNameController = TextEditingController();
  final TextEditingController _notesController = TextEditingController();
  bool _isLoading = false;
  bool _isInMeeting = false;
  String _currentClient = "";

  Future<Position> _determinePosition() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('Location services are disabled.');
    }

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('Location permissions are denied');
      }
    }
    
    if (permission == LocationPermission.deniedForever) {
      throw Exception('Location permissions are permanently denied.');
    } 

    return await Geolocator.getCurrentPosition();
  }

  Future<void> _checkIn() async {
    if (_clientNameController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter the client name')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      Position position = await _determinePosition();
      
      await widget.attendanceService.checkInToClient(
        clientName: _clientNameController.text.trim(), 
        lat: position.latitude, 
        lon: position.longitude,
      );

      if (!mounted) return;
      setState(() {
        _isInMeeting = true;
        _currentClient = _clientNameController.text.trim();
        _isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Successfully checked in at $_currentClient')),
      );
    } on ApiException catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('API Error: ${e.message}')),
      );
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    }
  }

  Future<void> _checkOut() async {
    setState(() => _isLoading = true);

    try {
      await widget.attendanceService.checkOutOfClient(_notesController.text.trim());

      if (!mounted) return;
      setState(() {
        _isInMeeting = false;
        _currentClient = "";
        _clientNameController.clear();
        _notesController.clear();
        _isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Successfully checked out of meeting.')),
      );
    } on ApiException catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('API Error: ${e.message}')),
      );
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    }
  }

  @override
  void dispose() {
    _clientNameController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Client Site Visits'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: _isLoading 
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView( // Added to prevent keyboard overflow
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 40),
                  if (!_isInMeeting) ...[
                    const Icon(Icons.business_center, size: 80, color: Colors.blueGrey),
                    const SizedBox(height: 24),
                    TextField(
                      controller: _clientNameController,
                      decoration: const InputDecoration(
                        labelText: 'Client Name',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.person),
                      ),
                    ),
                    const SizedBox(height: 24),
                    ElevatedButton.icon(
                      onPressed: _checkIn,
                      icon: const Icon(Icons.location_on),
                      label: const Text('Check In to Meeting'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    ),
                  ] else ...[
                    const Icon(Icons.meeting_room, size: 80, color: Colors.green),
                    const SizedBox(height: 16),
                    const Text(
                      'Meeting in progress with:',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 16, color: Colors.grey),
                    ),
                    Text(
                      _currentClient,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 32),
                    TextField(
                      controller: _notesController,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        labelText: 'Meeting Notes / Next Steps',
                        border: OutlineInputBorder(),
                        alignLabelWithHint: true,
                      ),
                    ),
                    const SizedBox(height: 24),
                    ElevatedButton.icon(
                      onPressed: _checkOut,
                      icon: const Icon(Icons.check_circle),
                      label: const Text('Check Out & Save Notes'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.redAccent,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    ),
                  ],
                ],
              ),
            ),
      ),
    );
  }
}