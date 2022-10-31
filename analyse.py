import numpy as np
import matplotlib.pyplot as plt


def skip_header(fname):
    with open(fname) as f:
        next(f)
        for row in f:
            yield row

def get_breathing_spans(time, breaths):
    n = time.shape[0]
    i = 0
    spans = []
    while i < n:
        a, b = 0, 0
        if breaths[i] != 0:
            a = time[i]
            if breaths[i]==1:
                color = 'green'
            else:
                color = 'red'
            while i < n-1 and breaths[i] != 0:
                i += 1
            b = time[i]
            if b > a:
                spans.append((a, b, color))
        i += 1
    return spans


fname = 'practices/3min 2022-10-30 18.28.59.716489.txt'

data = np.loadtxt(skip_header(fname), delimiter=';', )


t = data[:, 0]
t = (t - t.min()) / 60
hr = data[:, 1]
hrv = data[:, 3] # rmssd
print(hrv.mean())
breaths = data[:, -1].astype('int')

plt.figure(figsize=(12, 7))
plt.plot(t, hr)
#plt.plot(t, hrv)
spans = get_breathing_spans(t, breaths)
for span in spans:
    plt.axvspan(span[0], span[1], alpha=0.3, color=span[2])


plt.xlabel('Time (minutes)')
plt.ylabel('Heart rate (BPM)')
#plt.ylabel('HRV (ms)')
#plt.ylim((0, 100))
#plt.legend(['HRV (rmssd)'])
plt.show()