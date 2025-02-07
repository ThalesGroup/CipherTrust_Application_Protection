/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package io.trino.plugin.thales;
import com.ingrian.internal.ilc.IngrianLogService;

public class CustomLogger
        implements IngrianLogService
{
    @Override
    public void debug(String arg0)
    {
    }

    @Override
    public void debug(String arg0, Throwable arg1)
    {
        System.out.println("CustomLogger: WARN: " + arg0);
    }

    @Override
    public void error(String arg0)
    {
    }

    @Override
    public void error(String arg0, Throwable arg1)
    {
    }

    @Override
    public void info(String arg0)
    {
    }

    @Override
    public boolean isDebugEnabled()
    {
        return false;
    }

    @Override
    public boolean isErrorEnabled()
    {
        return false;
    }

    @Override
    public boolean isInfoEnabled()
    {
        return false;
    }

    @Override
    public boolean isTraceEnabled()
    {
        return false;
    }

    @Override
    public boolean isWarnEnabled()
    {
        return false;
    }

    @Override
    public void trace(String arg0)
    {
    }

    @Override
    public void warn(String arg0)
    {
    }

    @Override
    public void warn(String arg0, Throwable arg1)
    {
    }
}
