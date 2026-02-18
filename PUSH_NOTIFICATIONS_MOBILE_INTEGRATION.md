# Push Notifications - Mobile App Integration Guide

## Overview
The Belle House backend supports Firebase Cloud Messaging (FCM) for real-time push notifications to mobile clients. Notifications are automatically sent for project updates, invoices, and payment confirmations.

---

## 1. Setup Firebase in Your Mobile App

### For React Native (Expo)
```bash
npx expo install expo-notifications
# OR for bare React Native
npm install @react-native-firebase/app @react-native-firebase/messaging
```

### For Flutter
```yaml
# pubspec.yaml
dependencies:
  firebase_messaging: ^14.7.0
  firebase_core: ^2.24.0
```

---

## 2. Get FCM Token

### React Native (Expo)
```javascript
import * as Notifications from 'expo-notifications';

async function registerForPushNotifications() {
  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== 'granted') {
    console.log('Permission not granted');
    return;
  }
  
  const token = (await Notifications.getExpoPushTokenAsync()).data;
  return token;
}
```

### Flutter
```dart
import 'package:firebase_messaging/firebase_messaging.dart';

Future<String?> getFCMToken() async {
  FirebaseMessaging messaging = FirebaseMessaging.instance;
  
  // Request permission
  NotificationSettings settings = await messaging.requestPermission();
  
  if (settings.authorizationStatus == AuthorizationStatus.authorized) {
    String? token = await messaging.getToken();
    return token;
  }
  return null;
}
```

---

## 3. Send Token to Backend

### API Endpoint
```
POST /api/app/fcm-token/
```

### Headers
```
Authorization: Bearer <user_jwt_access_token>
Content-Type: application/json
```

### Request Body
```json
{
  "fcm_token": "your-device-fcm-token-here"
}
```

### Example Implementation (JavaScript)
```javascript
async function sendFCMToken(fcmToken, accessToken) {
  try {
    const response = await fetch('https://api2.bellehouseniger.com/api/app/fcm-token/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        fcm_token: fcmToken
      })
    });
    
    if (response.ok) {
      console.log('FCM token registered successfully');
    }
  } catch (error) {
    console.error('Failed to register FCM token:', error);
  }
}
```

### Example Implementation (Flutter/Dart)
```dart
Future<void> sendFCMToken(String fcmToken, String accessToken) async {
  final response = await http.post(
    Uri.parse('https://api2.bellehouseniger.com/api/app/fcm-token/'),
    headers: {
      'Authorization': 'Bearer $accessToken',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'fcm_token': fcmToken}),
  );
  
  if (response.statusCode == 200) {
    print('FCM token registered successfully');
  }
}
```

---

## 4. When to Register Token

Call the token registration in these scenarios:

1. **After successful login** - Register token immediately after user logs in
2. **On app startup** - If user is already logged in, register on app launch
3. **On token refresh** - FCM tokens can change, so listen for updates:

### React Native
```javascript
// Listen for token updates
Notifications.addPushTokenListener((token) => {
  sendFCMToken(token.data, userAccessToken);
});
```

### Flutter
```dart
FirebaseMessaging.instance.onTokenRefresh.listen((newToken) {
  sendFCMToken(newToken, userAccessToken);
});
```

---

## 5. Notification Types

The backend automatically sends push notifications for these events:

### 📸 Project Update Notification
**When:** Admin posts a new project update with photos/videos  
**Title:** "Nouvelle Mise à Jour - [Project Name]"  
**Body:** Update description  
**Data:**
```json
{
  "type": "project_update",
  "project_id": "123",
  "update_id": "456"
}
```

### 💰 New Invoice Notification
**When:** Admin creates a new invoice  
**Title:** "Nouvelle Facture"  
**Body:** "Facture #[number] - [amount] F CFA"  
**Data:**
```json
{
  "type": "invoice",
  "invoice_id": "789"
}
```

### ✅ Payment Confirmation
**When:** Admin marks an invoice as paid  
**Title:** "Paiement Reçu"  
**Body:** "Merci! Paiement de [amount] F CFA confirmé."  
**Data:**
```json
{
  "type": "payment_confirmation",
  "invoice_id": "789"
}
```

---

## 6. Handle Incoming Notifications

### React Native (Expo)
```javascript
import * as Notifications from 'expo-notifications';

// Configure notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

// Listen for notifications when app is in foreground
Notifications.addNotificationReceivedListener(notification => {
  const data = notification.request.content.data;
  
  switch(data.type) {
    case 'project_update':
      // Navigate to project details
      navigation.navigate('ProjectDetails', { projectId: data.project_id });
      break;
    case 'invoice':
      // Navigate to invoice
      navigation.navigate('Invoices', { invoiceId: data.invoice_id });
      break;
    case 'payment_confirmation':
      // Show success message
      showPaymentConfirmation();
      break;
  }
});

// Handle notification tap (when app is in background/closed)
Notifications.addNotificationResponseReceivedListener(response => {
  const data = response.notification.request.content.data;
  // Handle navigation based on data.type
});
```

### Flutter
```dart
import 'package:firebase_messaging/firebase_messaging.dart';

// Handle foreground messages
FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  print('Got a message: ${message.notification?.title}');
  
  if (message.data['type'] == 'project_update') {
    // Navigate to project details
    Navigator.pushNamed(context, '/project', 
      arguments: {'projectId': message.data['project_id']});
  }
});

// Handle notification tap (background/terminated)
FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
  // Handle navigation based on message.data['type']
});

// Handle notification when app is terminated
RemoteMessage? initialMessage = await FirebaseMessaging.instance.getInitialMessage();
if (initialMessage != null) {
  // Handle initial notification
}
```

---

## 7. Testing

### Test Token Registration
1. Login to the mobile app
2. Check that FCM token is sent to backend
3. Verify in backend that `ClientProfile.fcm_token` is saved

### Test Notifications
1. Have admin create a project update via admin dashboard
2. Check if notification appears on mobile device
3. Tap notification and verify navigation works

### Debug Tips
- Check if notification permissions are granted
- Verify FCM token is not empty before sending
- Test on real device (push notifications don't work on simulators for iOS)
- Check backend logs for notification sending status

---

## 8. API Base URL

**Production:** `https://api2.bellehouseniger.com`  
**Development:** Update based on your local setup

---

## 9. Project Phases Reference

When displaying project information, these are the phase codes and progress percentages:

| Phase Code | Display Name | Progress % |
|------------|--------------|------------|
| CONCEPTION | Conception et Démarches | 5% |
| IMPLANTATION | Implantation | 8% |
| FONDATIONS | Fondations | 23% |
| ELEVATION_MURS | Élévation des Murs | 41% |
| DALLE | Dalle et Acrotère | 57% |
| CREPISSAGE | Crépissage | 65% |
| ELECTRICITE_PLOMBERIE | Électricité & Plomberie | 81% |
| RESEAUX | Réseaux et Sécurité | 87% |
| CARRELAGE_PLAFOND | Carrelage & Plafonnage | 94% |
| PEINTURE_MENUISERIE | Peinture & Menuiserie | 99% |
| EXTERIEUR | Aménagements Extérieurs | 100% |

---

## Support

For API issues or questions, contact the backend team.
