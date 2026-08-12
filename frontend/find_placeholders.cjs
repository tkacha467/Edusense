const fs = require('fs');
const path = require('path');

function walk(dir) {
    let results = [];
    const list = fs.readdirSync(dir);
    list.forEach(function(file) {
        file = path.join(dir, file);
        const stat = fs.statSync(file);
        if (stat && stat.isDirectory()) { 
            results = results.concat(walk(file));
        } else { 
            if(file.endsWith('.tsx') || file.endsWith('.ts')) {
                results.push(file);
            }
        }
    });
    return results;
}

const files = walk('d:/Personal Knowledge Decay Predictor/frontend/src');

files.forEach(file => {
    const content = fs.readFileSync(file, 'utf8');
    const lines = content.split('\n');
    lines.forEach((line, i) => {
        // Find href="#" or to="#"
        if (line.includes('href=\"#\"') || line.includes('to=\"#\"')) {
            console.log(`[LINK] ${file}:${i+1}: ${line.trim()}`);
        }
        // Find empty onClick
        if (line.match(/onClick=\{\s*\(\)\s*=>\s*\{\s*\}\s*\}/) || line.match(/onClick=\{\s*\(\)\s*=>\s*console\.log/)) {
            console.log(`[ONCLICK] ${file}:${i+1}: ${line.trim()}`);
        }
        // Naive button check
        if (line.match(/<Button/i) && !line.includes('onClick') && !line.includes('type=\"submit\"') && !line.includes('type=\"button\"') && !line.includes('asChild') && !line.match(/<Button.*\{.*\}.*>/) && !line.includes('variant=')) {
            let hasAction = false;
            for(let j=0; j<4; j++) {
                if(lines[i+j] && (lines[i+j].includes('onClick') || lines[i+j].includes('type=\"submit\"') || lines[i+j].includes('type=\"button\"'))) {
                    hasAction = true;
                    break;
                }
            }
            if(!hasAction) {
                console.log(`[BUTTON] ${file}:${i+1}: ${line.trim()}`);
            }
        }
        
        // Let's also find <button without actions
        if (line.match(/<button/i) && !line.includes('onClick') && !line.includes('type=\"submit\"') && !line.includes('type=\"button\"') && !line.includes('disabled')) {
            let hasAction = false;
            for(let j=0; j<4; j++) {
                if(lines[i+j] && (lines[i+j].includes('onClick') || lines[i+j].includes('type=\"submit\"') || lines[i+j].includes('type=\"button\"'))) {
                    hasAction = true;
                    break;
                }
            }
            if(!hasAction) {
                console.log(`[button] ${file}:${i+1}: ${line.trim()}`);
            }
        }
    });
});
