import React from 'react';
import './App.css';

const App = () => {
    return(
        <div className = "App">
            <aside className = "sidebar">
                {/*sidebar content*/}
                <nav>
                    <ul>
                        <li><a href="#link1">Link 1</a></li>
                        <li><a href="#link2">Link 2</a></li>
                        <li><a href="#link3">Link 3</a></li>
                    </ul>
                </nav>
            </aside>
            <main className="main-content">
                <div className="search-bar">
                    {/* Full Width search bar */}
                    <input type="text" placeholder="Search..."/> 
                </div>
                <div className = "content-area">
                    {/* Two columns with paragraphs */}
                    <div className = "column nav">
                        <p>This is some text for the first column. it could be a long paragraph with more details.</p>
                    </div>
                    <div className = "column">
                        <p>This is some text for the second column.</p>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;