# Dashboard-Helper

Welcome to a mini project to help people explore both plotly and their data. I began this project because I struggled with understanding how to interact with all the available charts that exist through plotly.

---

To run, just run the app.py file and navigate to the webpage that it is hosted on.

![image](https://user-images.githubusercontent.com/82055130/202308858-59ee8fc1-ce29-4877-a706-ff7e2e3ff854.png)

From there, you can drag and drop or upload xlsx or csv files to create data to populate the charts.

Once data has been uploaded, "Edit Chart Details" offers all px charting options, when selected, three dropdowns will be populated.



https://user-images.githubusercontent.com/82055130/202311020-3b63e557-3f68-4770-84d5-dcf38a766028.mov



The first will have info from plotly linked so that you can reference the documents quickly and directly.
The second will have all the options that the particular chart can be populated to alter the chart.
The third will give all the optional layout arguments that you can use.

_**note:**_ On the second and third dropdown, you may need to enter dictionaries or lists exactly how you'd encode them into python.

Once all desired options are populated, you can now make changes, this will populate the chart if it rendered properly.

You can see the chart in the area below the buttons. Show function will demonstrate how to replicate this call via px figures and update layout. Another set of code will represent what arguments were passed to the function, _makeCharts_. This particular function is useful in the sense that all you have to do is pass it a dictionary with "chart", "figure", "layout" keys and it will recreate the desired chart.

If the chart errors out, a new button will show up that will allow you to see the traceback message for where the function broke.

![Screen Shot 2022-11-16 at 5 34 39 PM](https://user-images.githubusercontent.com/82055130/202309350-df36f150-2d1b-46cc-987d-4bc62774d4d8.png)

Please enjoy!
