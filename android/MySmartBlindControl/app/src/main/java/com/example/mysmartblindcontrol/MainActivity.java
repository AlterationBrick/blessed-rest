package com.example.mysmartblindcontrol;

import androidx.appcompat.app.AppCompatActivity;

import android.annotation.SuppressLint;
import android.app.TimePickerDialog;
import android.os.AsyncTask;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TimePicker;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.sql.Time;
import java.util.Calendar;

public class MainActivity extends AppCompatActivity {

    String ipaddr = "0.0.0.0:0";
    EditText startTime;

    @SuppressLint("ClickableViewAccessibility")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button tiltUp = findViewById(R.id.tiltUp);
        Button tiltDown = findViewById(R.id.tiltDown);
        Button tiltAuto = findViewById(R.id.tiltAuto);
        Button testLamp = findViewById(R.id.testLamp);
        EditText ipField = findViewById(R.id.editText);
        startTime = findViewById(R.id.startTime);
        ipField.addTextChangedListener(watch);



        tiltUp.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if (event.getAction() == MotionEvent.ACTION_DOWN) {
                    new Background_get().execute("tilt/up");
                } else if (event.getAction() == MotionEvent.ACTION_UP) {
                    new Background_get().execute("tilt/stop");
                }
                return true;
            }
        });

        tiltDown.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if (event.getAction() == MotionEvent.ACTION_DOWN) {
                    new Background_get().execute("tilt/down");
                } else if (event.getAction() == MotionEvent.ACTION_UP) {
                    new Background_get().execute("tilt/stop");
                }
                return true;
            }
        });

        tiltAuto.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if (event.getAction() == MotionEvent.ACTION_DOWN)
                    new Background_get().execute("tilt/auto");
                return true;
            }
        });

        testLamp.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if (event.getAction() == MotionEvent.ACTION_DOWN)
                    new Background_get().execute("lamp/on");
                return true;
            }
        });

        startTime.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch (View v, MotionEvent event) {
                if (event.getAction() == MotionEvent.ACTION_UP) {
                    Calendar mCurrentTime = Calendar.getInstance();
                    final int hour = mCurrentTime.get(Calendar.HOUR_OF_DAY);
                    int minute = mCurrentTime.get(Calendar.MINUTE);
                    TimePickerDialog mTimePicker;
                    mTimePicker = new TimePickerDialog(MainActivity.this, new TimePickerDialog.OnTimeSetListener() {
                        @Override
                        public void onTimeSet(TimePicker view, int hourOfDay, int minute) {
                            startTime.setText(String.format("%02d:%02d", hourOfDay, minute));
                            new Background_get().execute(String.format("begin/%d/%d", hourOfDay, minute));
                        }
                    }, hour, minute, true);
                    mTimePicker.setTitle("Select Time");
                    mTimePicker.show();
                }
                return true;
            }
        });
    }

    TextWatcher watch = new TextWatcher() {
        @Override
        public void beforeTextChanged(CharSequence s, int start, int count, int after) {

        }

        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {
            ipaddr = String.valueOf(s);
        }

        @Override
        public void afterTextChanged(Editable s) {

        }
    };



    private class Background_get extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... params) {
            try {
                // Define URL
                URL url = new URL("http://" + ipaddr + "/" + params[0]);
                // Open HTTP connection
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                // Create reader, string builder, and string to hold output
                BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                StringBuilder result = new StringBuilder();
                String inputLine;
                // Read lines from input
                while ((inputLine = in.readLine()) != null)
                    result.append(inputLine).append("\n");
                // Close buffered reader and disconnect HTTP connection
                in.close();
                connection.disconnect();
                // Return string of result
                return result.toString();
            } catch (IOException e) {
                e.printStackTrace();
            }
            return null;
        }
    }
}
