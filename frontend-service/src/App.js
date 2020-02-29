import React, { Suspense } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Page } from './Page.js'
import { UserProvider } from './authentication/UserContext.js';
import { WindowScrollProvider } from './WindowScrollContext.js';
import { SightingProvider } from './sighting/SightingContext.js';
import { BirdsProvider } from './bird/BirdsContext.js';
import SuspenseLoader from './suspense/SuspenseLoader';

export const App = ({ version }) => {
  prepareLocalStorage(version);

  return (
    <BrowserRouter>
      <WindowScrollProvider>
        <UserProvider>
          <BirdsProvider>
            <SightingProvider>
              <Suspense fallback={<SuspenseLoader />}>
                <Page />
              </Suspense>
            </SightingProvider>
          </BirdsProvider>
        </UserProvider>
      </WindowScrollProvider>
    </BrowserRouter>
  );
}

/**
 * Iff the provided version differs from previously set app version in local
 * storage, clears the local storage and updates the app version.
 */
function prepareLocalStorage(version) {
  const key = 'appVersion';
  const storedVersion = localStorage.getItem(key);
  if (!storedVersion || storedVersion !== version) {
    localStorage.clear();
    localStorage.setItem(key, version);
  }
}
